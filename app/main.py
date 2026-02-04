"""
FastAPI application entry point.
Registers middleware, exception handlers and routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import engine, Base
from app.routes import auth, items
from app.middleware import (
    RequestLoggingMiddleware,
    IdempotencyMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    LoginAttemptMiddleware,
    RequestSizeMiddleware
)
from app.exception import (
    APIException,
    api_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from fastapi.exceptions import RequestValidationError

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project A - Backend API")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"]
)

# Security and request middlewares (runs bottom to top)
app.add_middleware(RequestSizeMiddleware, max_size=1024 * 1024)  # 1MB limit
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window=60)
app.add_middleware(LoginAttemptMiddleware)
app.add_middleware(IdempotencyMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Register custom exception handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register routers
app.include_router(auth.router)
app.include_router(items.router)



@app.get("/")
def root():
    return {"message": "Welcome to Project A API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)