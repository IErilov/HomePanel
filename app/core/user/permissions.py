# permissions.py
import uuid
from db.database import get_db
from db.models.bucket import Buckets, BucketType
from db.models.user import AccountType, User
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.user.getters import get_current_user


def require_roles(*allowed_roles: AccountType):
    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.account_type not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения действия",
            )
        return current_user

    return role_checker