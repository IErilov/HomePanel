from sqlalchemy.ext.asyncio import AsyncSession

from repo.event import EventRepository
from models.event import Events, EventType

from datetime import datetime
from typing import List
import uuid

class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = EventRepository(db)

    async def create_event(self, event: Events):
        try:
            result = await self.repository.create(event)
            await self.db.commit()
            return result

        except Exception:
            await self.db.rollback()
            raise

    async def get_user_activity(
        self,
        user_id: uuid.UUID,
        limit: int) -> List[Events]:

        """получает все ивенты пользователя"""
        
        if limit < 1 or limit > 500:
            raise ValueError("Limit must be between 1 and 500")

        events = await self.repository.get_user_events(
            user_id=user_id,
            limit=limit
        )

        return events

    async def get_bucket_activity(
            self,
            bucket_name: str,
            limit: int) -> List[Events]:
    
            """получает все ивенты бакета"""
            
            if limit < 1 or limit > 500:
                raise ValueError("Limit must be between 1 and 500")
    
            events = await self.repository.get_buckets_events(
                bucket_name=bucket_name,
                limit=limit
            )
    
            return events

    async def get_general_stats(self, start: datetime, end: datetime):
        download = await self.repository.count_events_by_type(event_type=EventType.DOWNLOAD, start=start, end=end)
        delete = await self.repository.count_events_by_type(event_type=EventType.DELETE, start=start, end=end)
        upload = await self.repository.count_events_by_type(event_type=EventType.UPLOAD, start=start, end=end)

        all_events = await self.repository.count_events(start=start, end=end)

        return {
                "download": download,
                "upload": upload,
                "delete": delete,
                "all_events": all_events
               }
    