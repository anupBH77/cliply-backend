from app.models.features import Note
from app.schemas.schemas import NoteCreate
from app.db.db import db_dependency
from sqlalchemy import select
from fastapi import HTTPException, status,Request
from datetime import datetime
async def get_notes(
    user_id: int,
    db: db_dependency,
    request: Request,
):
    query_params = request.query_params
    if "archived" in query_params and query_params["archived"].lower() == "true":
        return await get_archived_notes(user_id=user_id, db=db)
    elif "deleted" in query_params and query_params["deleted"].lower() == "true":
        return await get_deleted_notes(user_id=user_id, db=db)
    result = await db.execute(
        select(Note).where(Note.user_id == user_id,
                           Note.is_deleted == False, Note.is_archived == False)
    )
    return result.scalars().all()
async def get_archived_notes(
    user_id: int,
    db: db_dependency,
):
    result = await db.execute(
        select(Note).where(Note.user_id == user_id,
                           Note.is_deleted == False, Note.is_archived == True)
    )
    return result.scalars().all()
async def get_deleted_notes(
    user_id: int,
    db: db_dependency,
):
    result = await db.execute(
        select(Note).where(Note.user_id == user_id,
                           Note.is_deleted == True)
    )
    return result.scalars().all()

async def get_note(
    note_id:any,
    user_id:any,
    db:db_dependency
):
    note = await db.scalar(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    return note

async def create_note(
    note_create: NoteCreate,
    user_id: int,
    db: db_dependency,
) -> Note:

    note = Note(
        title=note_create.title,
        content=note_create.content,
        collection_id=note_create.collection_id,
        user_id=user_id,
    )

    db.add(note)

    await db.commit()
    await db.refresh(note)

    return note

async def update_note(
    note_id: int,
    note_update: NoteCreate,
    user_id: int,
    db: db_dependency,
) -> Note:
    note = await db.scalar(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    note.title = note_update.title
    note.content = note_update.content
    note.collection_id = note_update.collection_id

    await db.commit()
    await db.refresh(note)

    return note

async def delete_note(
    note_id: int,
    user_id: int,
    db: db_dependency,
) -> None:
    note = await db.scalar(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    note.is_deleted = True
    note.deleted_at = datetime.utcnow()
    await db.commit()
    
async def archive_note(
    note_id: int,
    user_id: int,
    db: db_dependency,
) -> None:
    note = await db.scalar(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    note.is_archived = True
    await db.commit()
    
async def restore_note(
    note_id: int,
    user_id: int,
    db: db_dependency,
) -> None:
    note = await db.scalar(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    note.is_deleted = False
    note.deleted_at = None
    await db.commit()
    
async def unarchive_note(
    note_id: int,
    user_id: int,
    db: db_dependency,
) -> None:
    note = await db.scalar(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    note.is_archived = False
    await db.commit()