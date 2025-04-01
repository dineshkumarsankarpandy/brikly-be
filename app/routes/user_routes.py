from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.entities.user_entities import User
from app.core.db_setup import get_db
from app.models.users_models import UserLogin, UserRegister
from app.core.config import logging
from app.services.auth_service import create_access_token

router = APIRouter(prefix="/auth", tags=["User Authentication"])

@router.post("/register")
async def register_user(data: UserRegister, db:Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.mail == data.mail).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="user already exists")
    
    hashed_pass = User.hash_password(data.password)
    new_user = User(mail = data.mail, password = hashed_pass)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}


@router.post("/login")
async def login_user(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mail == data.mail).first()
    if not user or not User.verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid mail or password")
    
    token = create_access_token(data={"user_id": user.id, "email": user.mail})
    
    return {"message": "Login Successfull", "user_id": user.id, "email":user.mail,"access_token":token, "token_type": "bearer"}




