from datetime import datetime
import uuid
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from models.event import Events, EventType, EventStatus
from repo.event import EventsRepository


class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = EventsRepository(db)

    async def create_event(self, event: Events):
        try:
            result = await self.repository.create(event)
            await self.db.commit()
            return result
        except Exception:
            await self.db.rollback()
            raise

    async def get_event(self, event_id: uuid.UUID):
        return await self.repository.get_event(event_id)

    async def get_events(
        self,
        event_type: EventType | None = None,
        status: EventStatus | None = None,
        user_id: uuid.UUID | None = None,
        bucket_name: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Events]:
        if not 1 <= limit <= 500:
            raise ValueError("Limit must be between 1 and 500")
        if offset < 0:
            raise ValueError("Offset cannot be negative")
        if start_date is not None and end_date is not None and start_date > end_date:
            raise ValueError("start_date must be earlier than or equal to end_date")

        return await self.repository.get_events(
            event_type=event_type,
            status=status,
            user_id=user_id,
            bucket_name=bucket_name,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

    async def get_user_activity(self, user_id: uuid.UUID, limit: int = 50) -> List[Events]:
        if not 1 <= limit <= 500:
            raise ValueError("Limit must be between 1 and 500")
        return await self.repository.get_user_events(user_id=user_id, limit=limit)

    async def get_bucket_activity(self, bucket_name: str, limit: int = 50) -> List[Events]:
        if not 1 <= limit <= 500:
            raise ValueError("Limit must be between 1 and 500")
        return await self.repository.get_buckets_events(bucket_name=bucket_name, limit=limit)
