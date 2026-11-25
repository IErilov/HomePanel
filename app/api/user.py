from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from db.database import get_db
from db.models.user import AccountType, User
from core.user.getters import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from microservices.redis.services.rate_limit import rate_limit_for_user_login, rate_limit_for_user_create
router = APIRouter(
    prefix="/api/users",
    tags=["User API"],
)

# Полный путь к авторизации для Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/create", dependencies=[Depends(rate_limit_for_user_create())])
async def custom_create_user(
    name: str,
    password: str,
    email: str,
    account_type: AccountType,
    db: AsyncSession = Depends(get_db),
):
    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(
        password.encode("utf-8"),
        salt,
    ).decode("utf-8")

    user = User(
        name=name,
        password_hash=hash_password,
        email=email,
        account_type=account_type,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "account_type": user.account_type,
    }


@router.post("/login", dependencies=[Depends(rate_limit_for_user_login())])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    query = select(User).where(User.name == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not bcrypt.checkpw(
        form_data.password.encode("utf-8"),
        user.password_hash.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "role": current_user.account_type,
    }