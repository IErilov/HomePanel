from fastapi import Depends, Request, HTTPException
from redis.asyncio import Redis
from core.redis import get_redis


class RateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def check(
        self,
        key: str,
        limit: int = 120,
        window: int = 60
    ):
        script = """
        local count = redis.call('INCR', KEYS[1])
        if count == 1 then
            redis.call('EXPIRE', KEYS[1], ARGV[1])
        end
        local ttl = redis.call('TTL', KEYS[1])
        return {count, ttl}
        """

        count, ttl = await self.redis.eval(
            script, 1, key, window
        )

        if count > limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={"Retry-After": str(ttl)}
            )


def rate_limit(limit: int = 120, window: int = 60):
    async def dependency(
        request: Request,
        redis: Redis = Depends(get_redis)
    ):
        ip = request.client.host if request.client else "unknown"

        limiter = RateLimiter(redis)

        await limiter.check(
            key=f"rate_limit:{ip}:{request.url.path}",
            limit=limit,
            window=window
        )

    return dependency

def rate_limit_for_bucket(limit: int = 10, window: int = 60):
    async def dependency(
        request: Request,
        redis: Redis = Depends(get_redis)
    ):
        ip = request.client.host if request.client else "unknown"

        limiter = RateLimiter(redis)

        await limiter.check(
            key=f"rate_limit:bucket_creation:{ip}",
            limit=limit,
            window=window
        )

    return dependency

def rate_limit_for_user_login(limit: int = 10, window: int = 360):
    async def dependency(
        request: Request,
        redis: Redis = Depends(get_redis)
    ):
        ip = request.client.host if request.client else "unknown"

        limiter = RateLimiter(redis)

        await limiter.check(
            key=f"rate_limit:login:{request.url.path}",
            limit=limit,
            window=window
        )

    return dependency

def rate_limit_for_user_create(limit: int = 2, window: int = 360):
    async def dependency(
        request: Request,
        redis: Redis = Depends(get_redis)
    ):
        ip = request.client.host if request.client else "unknown"

        limiter = RateLimiter(redis)

        await limiter.check(
            key=f"rate_limit:create_user:{request.url.path}",
            limit=limit,
            window=window
        )

    return dependency