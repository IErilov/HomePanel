from sqlalchemy import func, select

from repo.event import EventsRepository
from models.event import Events, EventType
from datetime import datetime

class MonthAnalize:
    async def count_events_by_type(
        self,
        event_type: EventType,
        start_date: datetime,
        end_date: datetime) -> int:
        pass