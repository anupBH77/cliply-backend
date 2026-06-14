from fastapi import APIRouter,Depends
from app.services.tasksService import list_tasks,get_task,create_task,update_task
from app.db.db import db_dependency
from app.services.authService import authenticate_user
from app.models.users import User
from app.schemas.schemas import TaskCreate,TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/")
async def list_tasks_route(db: db_dependency, current_user: User = Depends(authenticate_user)):
    tasks = await list_tasks(user_id=current_user.id, db=db)
    return tasks

@router.get("/{task_id}")
async def get_task_route(task_id:str, db: db_dependency, current_user: User = Depends(authenticate_user)):
    task = await get_task(task_id=task_id, user_id=current_user.id, db=db)
    return task
@router.post("/")
async def create_task_route(task_data: TaskCreate, db: db_dependency, current_user: User = Depends(authenticate_user)):
    task = await create_task(user_id=current_user.id, task_data=task_data, db=db)
    return task

@router.patch("/{task_id}")
async def update_task_route(task_id: str, task_data: TaskUpdate, db: db_dependency, current_user: User = Depends(authenticate_user)):
    task = await update_task(task_id=task_id, user_id=current_user.id, task_data=task_data, db=db)
    return task

@router.patch("/{task_id}/status")
async def update_task_status_route(task_id: int, completed: bool):
    return {"id": task_id, "title": f"Task {task_id}", "completed": completed}

@router.delete("/{task_id}")
async def delete_task(task_id: int):
    return {"message": f"Task {task_id} deleted"}