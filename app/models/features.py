

from app.db.base import Base

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    collection_id: Mapped[int | None] = mapped_column(
        ForeignKey("collections.id"),
        nullable=True
    )

    title: Mapped[str] = mapped_column(String(255))

    content: Mapped[dict] = mapped_column(JSONB)

    collection: Mapped["Collection"] = relationship(
        back_populates="notes"
    )
    
class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    name: Mapped[str] = mapped_column(String(255))

    notes: Mapped[list["Note"]] = relationship(
        back_populates="collection"
    )