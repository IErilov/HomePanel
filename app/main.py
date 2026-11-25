from contextlib import asynccontextmanager
import os
from core.admin import AdminAuth, BucketAdmin, UserAdmin
from api.storage import router as storage_router
from api.user import router as user_router
import bcrypt
from db.database import async_session, engine, Base
from db.models.user import AccountType, User
from db.models.user import User
from microservices.events.models import event
from core.redis import redis_client
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from sqlalchemy import select
from microservices.redis.services.rate_limit import rate_limit
from microservices.redis.services.security_guard import security_guard

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis_client
    await app.state.redis.aclose()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as db:
        result = await db.execute(
            select(User).where(User.account_type == AccountType.SUPER_USER)
        )
        admin_exists = result.scalar_one_or_none()

        if not admin_exists:
            admin_name = os.getenv("FIRST_ADMIN_NAME", "admin")
            admin_password = os.getenv("FIRST_ADMIN_PASSWORD", "admin123")
            admin_email = os.getenv("FIRST_ADMIN_EMAIL", "admin@example.com")

            hashed = bcrypt.hashpw(
                admin_password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            first_admin = User(
                name=admin_name,
                password_hash=hashed,
                email=admin_email,
                account_type=AccountType.SUPER_USER,
                is_approved=True,
            )

            db.add(first_admin)
            await db.commit()
            print(f"Создан первый администратор: {admin_name}")

    yield

app = FastAPI(
    dependencies=[Depends(rate_limit(limit=120, window=60)), Depends(security_guard)],
    lifespan=lifespan
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(storage_router)
app.include_router(user_router)

auth_backend = AdminAuth(
    secret_key=os.getenv("ADMIN_SECRET_KEY", "super-secret-admin-key")
)
admin = Admin(app=app, engine=engine, authentication_backend=auth_backend)

admin.add_view(UserAdmin)
admin.add_view(BucketAdmin)
