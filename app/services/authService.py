from datetime import datetime, timedelta
import random
from fastapi import HTTPException, status,Response,Request
from sqlalchemy import select
from passlib.context import CryptContext

from app.models.users import User
from app.models.otp import OTP
from app.schemas.schemas import UserCreate,UserLogin,OTPCreate
from app.db.db import db_dependency
from app.services.mailService import GMailService
from app.services.JWTService import create_access_token,verify_token
from app.config.env_config import ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


async def register_user(
    user_create: UserCreate,
    db: db_dependency,
):
    mail_service = GMailService()
   
    # Check if email already exists
    existing_user = await db.scalar(
        select(User).where(User.email == user_create.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password
    password_hash = pwd_context.hash(user_create.password)

    # Create user
    user = User(
        email=user_create.email,
        password_hash=password_hash,
        is_verified=False,
    )

    db.add(user)

    # Generate OTP
    otp = str(random.randint(100000, 999999))

    # Delete old OTPs
    existing_otps = await db.execute(
        select(OTP).where(OTP.email == user_create.email)
    )

    for otp_record in existing_otps.scalars().all():
        await db.delete(otp_record)

    # Save OTP
    otp_record = OTP(
        email=user_create.email,
        otp_hash=pwd_context.hash(otp),
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )

    db.add(otp_record)

    await db.commit()
    await db.refresh(user)

    mail_service = GMailService()
    # Send email
    await mail_service.send_emails(
        subject="Verify your email",
        body_html=f"""
            <p>Thank you for registering. Please use the following OTP to verify your email:</p>
            <h2>{otp}</h2>
            <p>This OTP will expire in 10 minutes.</p>
        """,
        recipients=[user.email],
    )

    return {
        "message": "Registration successful. Please verify your email.",
        "email": user.email,
    }

async def verify_email_using_otp(payload: OTPCreate, db: db_dependency):
    otp_record = await db.scalar(
        select(OTP).where(OTP.email == payload.email)
    )

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP found for this email",
        )

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired",
        )

    if not pwd_context.verify(payload.otp, otp_record.otp_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP",
        )

    user = await db.scalar(
        select(User).where(User.email == payload.email)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.is_verified = True
    await db.delete(otp_record)
    await db.commit()

    return {"message": "Email verified successfully"}

async def login_user(db: db_dependency,user_login:UserLogin,response:Response ):
    user = await db.scalar(
        select(User).where(User.email == user_login.email)
    )

    if not user:
        return None

    if not pwd_context.verify(user_login.password, user.password_hash):
        return None
    access_token = create_access_token(user.id)

    response.set_cookie(
        "auth_id", access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return user

async def authenticate_user(db: db_dependency, request:Request):
    auth_id = request.cookies.get("auth_id")
   
    if not auth_id:
        return None
    user_id = verify_token(auth_id, "access")
    if not user_id:
        return None
    user = await db.scalar(
        select(User).where(User.id == user_id)
    )
    return user