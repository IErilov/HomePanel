from sqlalchemy.ext.asyncio import AsyncSession
from models.event import Events, EventType
from sqlalchemy import select, func
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

    async def get_recent_activity(self, limit: int=50) -> List[Events]:
            query = (select(Events).limit(limit).order_by(Events.created_at.desc()))
            result = await self.db.execute(query)
            events = result.scalars().all()
            
            return events

    async def count_events(self, start: datetime, end: datetime) -> int:
            query = (select(func.count()).select_from(Events).where(Events.created_at >= start, Events.created_at <= end))
    
            result = await self.db.execute(query)
            count = result.scalar_one()
    
            return count

    async def count_events_by_users(self, start: datetime, end: datetime, user_id: uuid) -> int:
            """Получает колличество ивентов у пользователей по пользователю"""
            query = (select(func.count())
                    .select_from(Events)
                    .where(Events.created_at >= start, Events.created_at <= end)
                    .where(Events.user_id == user_id))
                
            result = await self.db.execute(query)
            count = result.scalar_one()
            
            return count

    async def count_events_by_bucket(self, start: datetime, end: datetime, bucket_name: str) -> int:
            """Получает колличество ивентов у пользователей по бакету"""
            query = (select(func.count())
                    .select_from(Events)
                    .where(Events.created_at >= start, Events.created_at <= end)
                    .where(Events.bucket_name == bucket_name))
                          
            result = await self.db.execute(query)
            count = result.scalar_one()
                          
            return count

    async def count_events_by_type_by_user(self, event_type: EventType, start: datetime, end: datetime, user_id: uuid) -> int:
            """Получает колличество ивентов по типу у пользователя"""
            query = (select(func.count())
                    .select_from(Events)
                    .where(Events.event_type == event_type)
                    .where(Events.created_at >= start,Events.created_at <= end)
                    .where(Events.user_id == user_id))
            
            result = await self.db.execute(query)
            count = result.scalar_one()
            
            return count

    async def count_events_by_type_by_bucket(self, event_type: EventType, start: datetime, end: datetime, bucket_name: str) -> int:
                """Получает колличество ивентов по типу у бакета"""
                query = (select(func.count())
                        .select_from(Events)
                        .where(Events.event_type == event_type)
                        .where(Events.created_at >= start,Events.created_at <= end)
                        .where(Events.bucket_name == bucket_name))
                
                result = await self.db.execute(query)
                count = result.scalar_one()
                
                return count

    async def count_events_by_type(self, event_type: EventType, start: datetime, end: datetime) -> int:
                """Получает колличество ивентов по типу"""
                query = (select(func.count())
                        .select_from(Events)
                        .where(Events.event_type == event_type)
                        .where(Events.created_at >= start,
                                Events.created_at <= end))
                
                result = await self.db.execute(query)
                count = result.scalar_one()
                
                return count

    async def get_uploaded_size_by_user(self, start: datetime, end: datetime):
        query = (select(Events.user_id, func.sum(Events.file_size))
                .where(Events.event_type == EventType.UPLOAD)
                .group_by(Events.user_id)
                .where(Events.created_at >= start,
                          Events.created_at <= end))
        result = await self.db.execute(query)
        events = result.all()
                    
        return events

    async def get_download_size_by_user(self, start: datetime, end: datetime):
            query = (select(Events.user_id, func.sum(Events.file_size))
                    .where(Events.event_type == EventType.DOWNLOAD)
                    .group_by(Events.user_id)
                    .where(Events.created_at >= start,
                              Events.created_at <= end))
            result = await self.db.execute(query)
            events = result.all()
                        
            return events

    async def get_total_uploaded_size(self, start: datetime, end: datetime):
        query = (select(func.sum(Events.file_size))
                .where(Events.event_type == EventType.UPLOAD)
                .where(Events.created_at >= start,
                          Events.created_at <= end))
        result = await self.db.execute(query)
        size = result.scalar_one()

        return size

    async def get_total_downloaded_size(self, start: datetime, end: datetime):
            query = (select(func.sum(Events.file_size))
                    .where(Events.event_type == EventType.DOWNLOAD)
                    .where(Events.created_at >= start,
                              Events.created_at <= end))
            result = await self.db.execute(query)
            size = result.scalar_one()

            return size