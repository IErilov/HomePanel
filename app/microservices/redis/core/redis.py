from redis.asyncio import Redis

redis_client = Redis.from_url(
    "redis://redis:6379",
    decode_responses=True
)

async def get_redis() -> Redis:
    return redis_client