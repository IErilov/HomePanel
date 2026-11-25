
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.event import EventService
from models.event import EventType, EventStatus


router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/")
async def get_events(
    event_type: EventType | None = None,
    status: EventStatus | None = None,
    user_id: uuid.UUID | None = None,
    bucket_id: uuid.UUID | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    service = EventService(db)

    return await service.get_events(
        event_type=event_type,
        status=status,
        user_id=user_id,
        bucket_id=bucket_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )


@router.get("/{event_id}")
async def get_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = EventService(db)

    event = await service.get_event(event_id)

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@router.get("/user/{user_id}")
async def get_user_events(
    user_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    service = EventService(db)
    return await service.get_user_activity(user_id, limit)


@router.get("/bucket/{bucket_id}")
async def get_bucket_events(
    bucket_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    service = EventService(db)
    return await service.get_bucket_activity(bucket_id, limit)
