from enum import Enum as PyEnum
import re
import uuid
from db.database import Base
from sqlalchemy import BigInteger, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class BucketType(PyEnum):
    PERSONAL = "personal"
    SOCIAL = "social"
    MEDIA = "media"
    OPEN = "open"


class Buckets(Base):
    __tablename__ = "buckets"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    bucket_type: Mapped[BucketType] = mapped_column(
        Enum(BucketType, name="bucket_type"), nullable=False
    )
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    quota_bytes: Mapped[int] = mapped_column(
        BigInteger, default=100 * 1024 * 1024, nullable=False
    )

    owner: Mapped["User"] = relationship("User")

    @property
    def quota_mb(self) -> int:
        return (self.quota_bytes or 0) // (1024 * 1024)

    @quota_mb.setter
    def quota_mb(self, value: int) -> None:
        if value is not None:
            self.quota_bytes = int(value) * 1024 * 1024

    @property
    def s3_name(self) -> str:
        uid = (
            self.owner.id
            if getattr(self, "owner", None)
            else self.owner_id or "shared"
        )
        raw = f"{uid}-{self.name}".lower()
        clean = re.sub(r"[^a-z0-9-]", "-", raw).strip("-")
        return clean[:63]