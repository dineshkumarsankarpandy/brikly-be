from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    mail: EmailStr
    password: str = Field(..., min_length=6, description="Password with a minimum length of 6 characters")

class UserLogin(BaseModel):
    mail: EmailStr
    password: str = Field(..., min_length=6, description="Password with a minimum length of 6 characters")

    