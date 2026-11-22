from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from repo.event import EventRepository
from models.event import EventType
from datetime import datetime

class MonthAnalize:
    def __init__(self, db: AsyncSession):
            self.db = db
            self.repository = EventRepository(db)


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
        