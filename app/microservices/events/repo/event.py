from datetime import datetime
import uuid
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.event import Events, EventType, EventStatus


class EventsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, event: Events):
        self.db.add(event)
        await self.db.flush()
        return event

    @staticmethod
    def _apply_period(query, start: datetime | None = None, end: datetime | None = None):
        if start is not None:
            query = query.where(Events.created_at >= start)
        if end is not None:
            query = query.where(Events.created_at <= end)
        return query

    async def get_event(self, event_id: uuid.UUID):
        result = await self.db.execute(
            select(Events).where(Events.id == event_id)
        )
        return result.scalar_one_or_none()

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
        query = select(Events)
        if event_type is not None:
            query = query.where(Events.event_type == event_type)
        if status is not None:
            query = query.where(Events.event_status == status)
        if user_id is not None:
            query = query.where(Events.user_id == user_id)
        if bucket_name is not None:
            query = query.where(Events.bucket_name == bucket_name)
        query = self._apply_period(query, start_date, end_date)
        query = query.order_by(Events.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_events_by_type(self, event_type: EventType, limit: int) -> List[Events]:
        return await self.get_events(event_type=event_type, limit=limit)

    async def get_user_events(self, user_id: uuid.UUID, limit: int) -> List[Events]:
        return await self.get_events(user_id=user_id, limit=limit)

    async def get_buckets_events(self, bucket_name: str, limit: int) -> List[Events]:
        return await self.get_events(bucket_name=bucket_name, limit=limit)

    async def get_events_by_period(self, start: datetime, end: datetime, limit: int) -> List[Events]:
        return await self.get_events(start_date=start, end_date=end, limit=limit)

    async def get_recent_activity(self, limit: int = 50) -> List[Events]:
        return await self.get_events(limit=limit)

    async def count_events(self, start: datetime | None = None, end: datetime | None = None) -> int:
        query = self._apply_period(select(func.count()).select_from(Events), start, end)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def count_events_by_type(
        self, event_type: EventType, start: datetime | None = None, end: datetime | None = None
    ) -> int:
        query = select(func.count()).select_from(Events).where(Events.event_type == event_type)
        query = self._apply_period(query, start, end)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def count_events_by_status(
        self, status: EventStatus, start: datetime | None = None, end: datetime | None = None
    ) -> int:
        query = select(func.count()).select_from(Events).where(Events.event_status == status)
        query = self._apply_period(query, start, end)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def count_events_by_users(
        self, user_id: uuid.UUID, start: datetime | None = None, end: datetime | None = None
    ) -> int:
        query = select(func.count()).select_from(Events).where(Events.user_id == user_id)
        query = self._apply_period(query, start, end)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def count_events_by_bucket(
        self, bucket_name: str, start: datetime | None = None, end: datetime | None = None
    ) -> int:
        query = select(func.count()).select_from(Events).where(Events.bucket_name == bucket_name)
        query = self._apply_period(query, start, end)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def count_events_by_type_by_user(
        self, event_type: EventType, start: datetime | None, end: datetime | None, user_id: uuid.UUID
    ) -> int:
        query = (
            select(func.count()).select_from(Events)
            .where(Events.event_type == event_type, Events.user_id == user_id)
        )
        query = self._apply_period(query, start, end)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def count_events_by_type_by_bucket(
        self, event_type: EventType, start: datetime | None, end: datetime | None, bucket_name: str
    ) -> int:
        query = (
            select(func.count()).select_from(Events)
            .where(Events.event_type == event_type, Events.bucket_name == bucket_name)
        )
        query = self._apply_period(query, start, end)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_uploaded_size_by_user(
        self, user_id: uuid.UUID, start: datetime | None = None, end: datetime | None = None
    ):
        query = select(func.coalesce(func.sum(Events.file_size), 0)).where(
            Events.event_type == EventType.UPLOAD, Events.user_id == user_id
        )
        query = self._apply_period(query, start, end)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_download_size_by_user(
        self, user_id: uuid.UUID, start: datetime | None = None, end: datetime | None = None
    ):
        query = select(func.coalesce(func.sum(Events.file_size), 0)).where(
            Events.event_type == EventType.DOWNLOAD, Events.user_id == user_id
        )
        query = self._apply_period(query, start, end)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_total_uploaded_size(self, start: datetime | None = None, end: datetime | None = None):
        query = select(func.coalesce(func.sum(Events.file_size), 0)).where(
            Events.event_type == EventType.UPLOAD
        )
        query = self._apply_period(query, start, end)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_total_downloaded_size(self, start: datetime | None = None, end: datetime | None = None):
        query = select(func.coalesce(func.sum(Events.file_size), 0)).where(
            Events.event_type == EventType.DOWNLOAD
        )
        query = self._apply_period(query, start, end)
        result = await self.db.execute(query)
        return result.scalar_one()
