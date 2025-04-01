import jwt
import bcrypt
from datetime import datetime, timedelta,timezone
from app.core.settings import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oAuth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")



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

def get_current_user(token: str = Depends(oAuth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload