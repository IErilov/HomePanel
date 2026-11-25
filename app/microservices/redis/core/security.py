from redis.asyncio import Redis


class SecurityService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def is_blocked(self, identifier: str) -> bool:
        return bool(await self.redis.exists(
            f"security:blocked:{identifier}"
        ))

    async def block(
        self,
        identifier: str,
        duration: int = 300
    ):
        await self.redis.set(
            f"security:blocked:{identifier}",
            "1",
            ex=duration
        )

    async def unblock(self, identifier: str):
        await self.redis.delete(
            f"security:blocked:{identifier}"
        )