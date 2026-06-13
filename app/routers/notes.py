from fastapi import APIRouter, Depends, status,Request
from app.schemas.schemas import NoteCreate
from app.services.notesService import create_note,update_note,get_note,get_notes
from app.db.db import db_dependency
from app.services.authService import authenticate_user
from app.models.users import User
router = APIRouter(prefix="/notes", tags=["Notes"])



@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_note_route(
    payload: NoteCreate,
    db: db_dependency,
    request: Request,
    current_user: User = Depends(authenticate_user),
):
    note = await create_note(
        note_create=payload,
        user_id=current_user.id,
        db=db,
    )

    return {
        "id": note.id,
        "title": note.title,
        "collection_id": note.collection_id,
    }
@router.get("/")
async def list_notes_route(db: db_dependency, request: Request, current_user: User = Depends(authenticate_user)):
    notes = await get_notes(user_id=current_user.id, db=db)
    return notes
@router.get("/{note_id}")
async def get_note_route(note_id: str, db: db_dependency, request: Request, current_user: User = Depends(authenticate_user)):

    note = await get_note(note_id=note_id, user_id=current_user.id, db=db)
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "collection_id": note.collection_id,
    }
@router.patch("/{note_id}")
async def update_note_route(note_id: str, payload: NoteCreate, db: db_dependency, request: Request, current_user: User = Depends(authenticate_user)):
    note = await update_note(note_id=note_id, note_update=payload, user_id=current_user.id, db=db)
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "collection_id": note.collection_id,
    }