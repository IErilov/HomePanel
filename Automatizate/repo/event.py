from sqlalchemy.ext.asyncio import AsyncSession
from models.event import Events, EventType
from sqlalchemy import select
from datetime import datetime

import uuid
from typing import List

class EventsRepository:
    def __init__(self, db: AsyncSession):
            self.db = db
    
    async def create(self, event: Events):
        self.db.add(event)
        await self.db.flush()
    
        return event

    async def get_events_by_type(self, event_type: EventType, limit: int) -> List[Events]:
        query = (select(Events)
                .where(Events.event_type == event_type)
                .order_by(Events.created_at.desc())
                .limit(limit))
        result = await self.db.execute(query)
        events = result.scalars().all()
         
        return events

    async def get_user_events(self, user_id: uuid.UUID, limit: int) -> List[Events]:
        query = (select(Events)
                .where(Events.user_id == user_id)
                .order_by(Events.created_at.desc())
                .limit(limit))
        result = await self.db.execute(query)
        events = result.scalars().all()

        return events

    async def get_buckets_events(self, bucket_name: str, limit: int) -> List[Events]:
        query = (select(Events)
                .where(Events.bucket_name == bucket_name)
                .order_by(Events.created_at.desc())
                .limit(limit))
        result = await self.db.execute(query)
        events = result.scalars().all()

        return events


    async def get_events_by_period(self, start: datetime, end: datetime, limit: int) -> List[Events]:
        query = (select(Events)
                .where(Events.created_at >= start,
                       Events.created_at <= end)
                .order_by(Events.created_at.desc())
                .limit(limit))
        result = await self.db.execute(query)
        events = result.scalars().all()
        
        return events