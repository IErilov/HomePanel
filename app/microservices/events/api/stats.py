import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from servicse.stats import Stats


router = APIRouter(prefix="/stats", tags=["Statistics"])


def validate_period(start: datetime | None, end: datetime | None):
    if start is not None and end is not None and start > end:
        raise HTTPException(status_code=422, detail="start must be earlier than or equal to end")


@router.get("/overview")
async def get_overview(
    start: datetime | None = None,
    end: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    validate_period(start, end)
    return await Stats(db).get_general_stats(start, end)


@router.get("/users/{user_id}")
async def get_user_statistics(
    user_id: uuid.UUID,
    start: datetime | None = None,
    end: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    validate_period(start, end)
    return await Stats(db).get_user_statistics(user_id, start, end)


@router.get("/buckets/{bucket_name}")
async def get_bucket_statistics(
    bucket_name: str,
    start: datetime | None = None,
    end: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    validate_period(start, end)
    return await Stats(db).get_bucket_statistics(bucket_name, start, end)
