from fastapi import APIRouter
from fastapi import Depends
from app.services.authService import authenticate_user
from app.services.collectionsService import get_collections,create_collection
from app.db.db import db_dependency
from app.models.users import User
from app.schemas.schemas import CollectionCreate
router = APIRouter(prefix="/collections", tags=["Collections"])

@router.get("/")
async def list_collections(db: db_dependency, current_user: User = Depends(authenticate_user)):
    collections = await get_collections(user_id=current_user.id, db=db)
    return collections

@router.post("/")
async def create_collection_route(collection_create: CollectionCreate, db: db_dependency, current_user: User = Depends(authenticate_user)):
    collection = await create_collection(user_id=current_user.id, name=collection_create.name, db=db)
    return {
        "id": str(collection.id),
        "name": collection.name
    }