from storage.minio_client import create_bucket
from db.models.bucket import BucketType, Buckets
import uuid
from db.database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def create_bucket_for_user(name: str, bucket_type: BucketType, user_id: uuid, db: AsyncSession = Depends(get_db)) -> Buckets:
    bucket = Buckets(name, bucket_type, user_id)
    create_bucket(name)

    db.add(bucket)
    await db.commit()
    await db.refresh(bucket)

    return bucket