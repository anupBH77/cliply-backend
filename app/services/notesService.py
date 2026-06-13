from app.models.features import Note
from app.schemas.schemas import NoteCreate
from app.db.db import db_dependency
from sqlalchemy import select
from fastapi import HTTPException, status

async def get_notes(
    user_id: int,
    db: db_dependency,
):
    result = await db.execute(
        select(Note).where(Note.user_id == user_id)
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