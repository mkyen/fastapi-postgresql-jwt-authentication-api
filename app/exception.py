"""
Custom exceptions and error handlers
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class APIException(HTTPException):
    """Base API exception"""

    def __init__(
            self,
            status_code: int,
            detail: str,
            error_code: str = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code or f"ERROR_{status_code}"


class UserAlreadyExistsException(APIException):
    """User already exists error"""

    def __init__(self, detail: str = "User already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="USER_EXISTS"
        )


class UserNotFoundException(APIException):
    """User not found error"""

    def __init__(self, detail: str = "User not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="USER_NOT_FOUND"
        )


class InvalidCredentialsException(APIException):
    """Invalid login credentials"""

    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="INVALID_CREDENTIALS"
        )


class ItemNotFoundException(APIException):
    """Item not found error"""

    def __init__(self, detail: str = "Item not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="ITEM_NOT_FOUND"
        )


# Error handlers
async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions"""
    logger.error(
        f"API Exception: {exc.error_code} - {exc.detail} "
        f"(Request: {request.url.path})"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail
            }
        }
    )


async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )