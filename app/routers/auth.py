# app/api/v1/auth.py

from fastapi import APIRouter, status
from app.schemas.schemas import UserCreate ,UserLogin,OTPCreate
from app.services.authService import register_user, authenticate_user,verify_email_using_otp
from app.db.db import db_dependency

from fastapi import HTTPException

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload:UserCreate,db:db_dependency):
    return await register_user(payload, db)

@router.post("/verify-email")
async def verify_email(payload: OTPCreate, db: db_dependency):
    return await verify_email_using_otp(payload, db)

@router.post("/login")
async def login(payload:UserLogin,db:db_dependency):
    user = await authenticate_user(db, payload)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return {"message": "User logged in successfully"}

