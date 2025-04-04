import jwt
import bcrypt
from datetime import datetime, timedelta,timezone
from app.core.settings import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.db_setup import get_db
from app.entities.user_entities import User
from app.core.config import logging
from fastapi.security import OAuth2PasswordBearer

oAuth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

http_bearer_scheme = HTTPBearer(auto_error=True)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=7)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm= settings.ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  
    except jwt.InvalidTokenError:
        return None  

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer_scheme), 
    db: Session = Depends(get_db) # Inject DB session
) -> User: # Return the actual User object
    """
    Verifies the JWT token from Bearer credentials and returns the User object.
    """
    token = credentials.credentials
    scheme = credentials.scheme
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )
    user_id = payload.get("user_id") 
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload (missing user_id)",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )

    logging.info(f"Authenticated user: {user.mail} (ID: {user.id})")
    return user