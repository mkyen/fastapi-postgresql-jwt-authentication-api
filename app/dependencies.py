
"""
Dependency injection for database sessions and authentication
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.auth import decode_token
from app.models import User

# HTTPBearer: automatically parses "Authorization: Bearer <token>" format
security = HTTPBearer()


def get_db():
    """
    Create database session for each request.
    Session is automatically closed after request completes.
    """
    db = SessionLocal()  # Open new session
    try:
        yield db  # Use during request
    finally:
        db.close()  # Close after request


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),  # Extract token
        db: Session = Depends(get_db)  # Get database session
) -> User:
    """
    Extract and validate JWT token, return authenticated user.

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials  # Extract token from "Bearer <token>"
    payload = decode_token(token)  # Decode JWT

    if payload is None:  # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    email = payload.get("sub")  # Extract email from token
    if email is None:  # No email in token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.email == email).first()  # Find user in DB
    if user is None:  # User not found
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user  # Return authenticated user


