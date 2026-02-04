"""
Middleware for logging, idempotency, request tracking,
rate limiting, security headers, login attempts and request size
"""
import time
import uuid
import logging
from collections import defaultdict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Idempotency store (in production, use Redis)
idempotency_store = {}

# Login attempts store (in production, use Redis)
login_attempts = defaultdict(lambda: {"count": 0, "locked_until": 0})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses"""

    async def dispatch(self, request: Request, call_next: Callable):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        logger.info(f"Request {request_id}: {request.method} {request.url.path}")
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(f"Response {request_id}: Status {response.status_code} Duration {duration:.3f}s")
        response.headers["X-Request-ID"] = request_id
        return response


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Idempotency for POST/PUT/PATCH requests"""

    async def dispatch(self, request: Request, call_next: Callable):
        if request.method in ["POST", "PUT", "PATCH"]:
            idempotency_key = request.headers.get("Idempotency-Key")
            if idempotency_key:
                if idempotency_key in idempotency_store:
                    logger.info(f"Idempotent request detected: {idempotency_key}")
                    cached = idempotency_store[idempotency_key]
                    return Response(content=cached["body"], status_code=cached["status_code"], headers=cached["headers"])

        response = await call_next(request)

        if request.method in ["POST", "PUT", "PATCH"]:
            idempotency_key = request.headers.get("Idempotency-Key")
            if idempotency_key:
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                idempotency_store[idempotency_key] = {"body": body, "status_code": response.status_code, "headers": dict(response.headers)}
                return Response(content=body, status_code=response.status_code, headers=dict(response.headers))

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limit number of requests per IP within a time window"""

    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable):
        client_ip = request.client.host
        now = time.time()
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.window]
        if len(self.requests[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(status_code=429, content={"error": "Too many requests. Try again later."})
        self.requests[client_ip].append(now)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security-related headers to all responses"""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        response.headers["Cache-Control"] = "no-store"
        return response


class LoginAttemptMiddleware(BaseHTTPMiddleware):
    """Track failed login attempts and lock after too many failures"""

    async def dispatch(self, request: Request, call_next: Callable):
        if request.url.path == "/auth/login" and request.method == "POST":
            client_ip = request.client.host
            now = time.time()
            if now < login_attempts[client_ip]["locked_until"]:
                logger.warning(f"Locked IP trying to login: {client_ip}")
                return JSONResponse(status_code=429, content={"error": "Too many failed attempts. Try again in 15 minutes."})

            response = await call_next(request)

            if response.status_code == 401:
                login_attempts[client_ip]["count"] += 1
                logger.warning(f"Failed login attempt {login_attempts[client_ip]['count']} for IP: {client_ip}")
                if login_attempts[client_ip]["count"] >= 5:
                    login_attempts[client_ip]["locked_until"] = now + 900
                    logger.warning(f"IP locked: {client_ip}")
            else:
                login_attempts[client_ip] = {"count": 0, "locked_until": 0}

            return response

        return await call_next(request)


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Reject requests that exceed maximum allowed body size"""

    def __init__(self, app, max_size: int = 1024 * 1024):
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next: Callable):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_size:
            logger.warning(f"Request too large: {content_length} bytes")
            return JSONResponse(status_code=413, content={"error": "Request body too large"})
        return await call_next(request)