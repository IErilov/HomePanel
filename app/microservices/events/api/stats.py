
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.stats import Stats


router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/overview")
async def get_overview(
    start: datetime | None = None,
    end: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    service = Stats(db)
    return await service.get_general_stats(start, end)


@router.get("/users/{user_id}")
async def get_user_statistics(
    user_id: uuid.UUID,
    start: datetime | None = None,
    end: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    service = Stats(db)
    return await service.get_user_statistics(user_id, start, end)


@router.get("/buckets/{bucket_name}")
async def get_bucket_statistics(
    bucket_name: str,
    start: datetime | None = None,
    end: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    service = Stats(db)
    return await service.get_bucket_statistics(bucket_name, start, end)
