from sqlalchemy.ext.asyncio import AsyncSession

from repo.event import EventRepository
from models.event import Events
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
        limit: int) -> List(Events):
        
        if limit < 1 or limit > 500:
            raise ValueError("Limit must be between 1 and 500")

        events = await self.repository.get_user_events(
            user_id=user_id,
            limit=limit
        )

        return events