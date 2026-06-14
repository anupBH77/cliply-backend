from pydantic import BaseModel, EmailStr
from typing import Optional,Dict, Any
from enum import Enum

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
    collection_id: Optional[str] = None
    
class CollectionCreate(BaseModel):
    name: str

class TaskStatusEnum(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
class TaskPriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = TaskStatusEnum.todo.value
    priority: Optional[str] = TaskPriorityEnum.medium.value

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
