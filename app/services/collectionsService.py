from app.db.db import db_dependency
from app.models.features import Collection
from sqlalchemy import select

async def get_collections(user_id:str, db: db_dependency):
    collections = await db.execute(select(Collection).where(Collection.user_id == user_id))
   
    collections_list = []
    for collection in collections.scalars().all():
        collections_list.append({
            "id": str(collection.id),
            "name": collection.name
        })
    return collections_list

async def create_collection(user_id:str, name:str, db: db_dependency):
    collection = Collection(
        user_id=user_id,
        name=name
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return collection