from enum import Enum as PyEnum

from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base

class AccountType(PyEnum):
    SUPER_USER = "super_user"
    FAMILY = "family"


class User(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    account_type: Mapped[AccountType] = mapped_column(
        Enum(AccountType, name="account_type"),
        nullable=False,
        default=AccountType.FAMILY,
    )

    is_approved: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )


    def __str__(self) -> str:
        return f"{self.name} ({self.email})"