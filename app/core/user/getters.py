import uuid
from db.database import get_db
from db.models.user import User
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt 
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/login", auto_error=False
)

async def get_user_by_id(user_id: uuid.UUID, db: AsyncSession):
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return {"name": user.name, "adress": user.adress}

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Неверный токен",
            )

        user_uuid = uuid.UUID(user_id)

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Токен недействителен или истёк",
        )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Некорректный ID в токене",
        )

    result = await db.execute(
        select(User).where(User.id == user_uuid)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Пользователь не найден",
        )

    return user


async def get_optional_user(
    token: str | None = Depends(
        optional_oauth2_scheme
    ),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not token:
        return None
    try:
        return await get_current_user(token=token, db=db)
    except HTTPException:
        return None