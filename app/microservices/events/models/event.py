from enum import Enum as PyEnum
import uuid

from sqlalchemy import String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from events.core.database import Base
from db.models.bucket import BucketType


class EventType(PyEnum):
    UPLOAD = "upload"
    DELETE = "delete"
    DOWNLOAD = "download"

class EventStatus(PyEnum):
    SUCCESS = "success"
    FAILED = "failed"
    DENIED = "denied"


class Events(Base):
    __tablename__ = "events"

    IP: Mapped[str] = mapped_column(
        String(45),
        nullable=False
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    user: Mapped["User | None"] = relationship(
        back_populates="events"
    )

    bucket_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    bucket_type: Mapped[BucketType] = mapped_column(
            Enum(BucketType, name="bucket_type"),
            nullable=False,
    )

    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="event_type"),
        nullable=False,
    )

    event_status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, name="event_status"),
        nullable=False,
    )

    object_name: Mapped[str] = mapped_column(
        nullable=False,
    )

    file_size: Mapped[int | None] = mapped_column(
        nullable=True
    )

    def __str__(self) -> str:
        return f"{self.IP} ({self.event_type})"