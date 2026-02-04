from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.auth import decode_token
from app.models import User

# HTTPBearer: "Authorization: Bearer <token>" formatını otomatik parse eder
security = HTTPBearer()


# get_db: Her request için database session oluşturur
def get_db():
    db = SessionLocal()  # Yeni session aç
    try:
        yield db  # Request sırasında kullan
    finally:
        db.close()  # Request bitince kapat


# get_current_user: Token'dan kullanıcıyı bulur
def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),  # Token'ı al
        db: Session = Depends(get_db)  # Database session al
) -> User:
    token = credentials.credentials  # "Bearer eyJhbGc..." → "eyJhbGc..."
    payload = decode_token(token)  # JWT decode et

    if payload is None:  # Token geçersiz
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    email = payload.get("sub")  # Token'dan email'i al
    if email is None:  # Email yok
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.email == email).first()  # DB'den user bul
    if user is None:  # User yok
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user  # Authenticated user döndür