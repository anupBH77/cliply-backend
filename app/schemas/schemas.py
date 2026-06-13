from pydantic import BaseModel, EmailStr
from typing import Optional,Dict, Any


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class OTPCreate(BaseModel):
    email: EmailStr
    otp: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    created_at: Optional[str]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class NoteCreate(BaseModel):
    title: str
    content: Dict[str, Any]
    collection_id: Optional[int] = None