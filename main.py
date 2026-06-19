from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.db import engine

from app.routers.auth import router as auth_router
from app.routers.notes import router as notes_router
from app.routers.collections import router as collections_router
from app.routers.tasks import router as tasks_router
from app.config.env_config import APP_URL
app = FastAPI(
    title="My API",
    version="1.0.0",
   
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        APP_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(notes_router)
app.include_router(collections_router)
app.include_router(tasks_router)
@app.get("/")
def root():
    return {"message": "Hello FastAPI"}