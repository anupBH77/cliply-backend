from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.env_config import DATABASE_URL
from fastapi import Depends
from typing import Annotated

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass


async def get_db():
    async with SessionLocal() as session:
        yield session
        
db_dependency = Annotated[AsyncSession, Depends(get_db)]