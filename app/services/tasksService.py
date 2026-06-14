from app.models.features import Task
from app.db.db import db_dependency
from sqlalchemy import select
from app.schemas.schemas import TaskCreate
from datetime import date
async def list_tasks(user_id:str, db: db_dependency):
    tasks = await db.execute(select(Task).where(Task.user_id == user_id))
    tasks_list = []
    for task in tasks.scalars().all():
        tasks_list.append({
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        })
    return tasks_list

async def get_task(task_id:str, user_id:str, db: db_dependency):
    task = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    task = task.scalar_one_or_none()
    if task is None:
        return None
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }

async def create_task(user_id:str, task_data: TaskCreate, db: db_dependency):
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        due_date=date.fromisoformat(task_data.due_date) if task_data.due_date else None,
        status=task_data.status,
        priority=task_data.priority
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }

async def update_task(task_id: str, user_id: str, task_data: TaskCreate, db: db_dependency):
    task = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    task = task.scalar_one_or_none()
    if task is None:
        return None
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.due_date is not None:
        task.due_date = date.fromisoformat(task_data.due_date)
    if task_data.status is not None:
        task.status = task_data.status
    if task_data.priority is not None:  
        task.priority = task_data.priority
    await db.commit()
    await db.refresh(task)
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }  
        