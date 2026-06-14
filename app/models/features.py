

from app.db.base import Base
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import DateTime, Text, func
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.schemas.schemas import TaskStatusEnum,TaskPriorityEnum
class Note(Base):
    __tablename__ = "notes"

    id: Mapped[UUID] = mapped_column(
    PG_UUID(as_uuid=True),
    primary_key=True,
    default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id")
    )

    collection_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("collections.id"),
        nullable=True
    )

    title: Mapped[str] = mapped_column(String(255))

    content: Mapped[dict] = mapped_column(JSONB)

    collection: Mapped["Collection"] = relationship(
        back_populates="notes"
    )
    
    created_at : Mapped[DateTime] = mapped_column(
        DateTime,
        default=func.now()
    )
    updated_at : Mapped[DateTime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )
    
class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[UUID] = mapped_column(
    PG_UUID(as_uuid=True),
    primary_key=True,
    default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id")
    )

    name: Mapped[str] = mapped_column(String(255))

    notes: Mapped[list["Note"]] = relationship(
        back_populates="collection"
    )
    
    created_at : Mapped[DateTime] = mapped_column(
        DateTime,
        default=func.now()
    )
    updated_at : Mapped[DateTime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )
    
class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(
    PG_UUID(as_uuid=True),
    primary_key=True,
    default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default=TaskStatusEnum.todo.value
    )

    due_date: Mapped[datetime | None] = mapped_column(
        nullable=True
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        default=TaskPriorityEnum.medium.value
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )