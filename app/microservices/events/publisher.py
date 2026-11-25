import uuid
from redis.asyncio import Redis


class EventPublisher:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def publish(
        self,
        event_type: str,
        user_id: str | None,
        bucket_id: str,
        object_name: str | None = None,
        file_size: int = 0,
        status: str = "SUCCESS"
    ):
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "user_id": user_id or "",
            "bucket_id": bucket_id,
            "object_name": object_name or "",
            "file_size": str(file_size),
            "status": status
        }

        await self.redis.xadd(
            "events:stream",
            event
        )