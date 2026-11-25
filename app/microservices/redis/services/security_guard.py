from fastapi import Request, Depends, HTTPException
from redis.asyncio import Redis

from core.redis import get_redis
from core.user.getters import get_optional_user
from db.models.user import User
from microservices.redis.core.security import SecurityService


async def security_guard(
    request: Request,
    redis: Redis = Depends(get_redis),
    user: User | None = Depends(get_optional_user)
):
    security = SecurityService(redis)

    ip = request.client.host if request.client else "unknown"

    identifiers = [f"ip:{ip}"]

    if user:
        identifiers.append(f"user:{user.id}")

    for identifier in identifiers:
        if await security.is_blocked(identifier):
            raise HTTPException(
                status_code=403,
                detail="Access temporarily blocked"
            )