
import uuid
from enum import Enum as PyEnum

from sqlalchemy import String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class BucketType(str, PyEnum):
    PERSONAL = "personal"
    SOCIAL = "social"
    MEDIA = "media"
    OPEN = "open"
    UNKNOWN = "unknown"


class EventType(PyEnum):
    UPLOAD = "upload"
    DELETE = "delete"
    DOWNLOAD = "download"
    RENAME = "rename"


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
        nullable=True
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
        String,
        nullable=False,
    )

    file_size: Mapped[int | None] = mapped_column(
        nullable=True
    )

    def __str__(self) -> str:
        return f"{self.IP} ({self.event_type})"
