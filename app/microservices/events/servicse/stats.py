from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from models.event import EventStatus, EventType
from repo.event import EventsRepository


class Stats:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = EventsRepository(db)

    async def get_general_stats(
        self, start: datetime | None = None, end: datetime | None = None
    ):
        if start is not None and end is not None and start > end:
            raise ValueError("start must be earlier than or equal to end")

        downloads = await self.repository.count_events_by_type(EventType.DOWNLOAD, start, end)
        uploads = await self.repository.count_events_by_type(EventType.UPLOAD, start, end)
        deletes = await self.repository.count_events_by_type(EventType.DELETE, start, end)
        total = await self.repository.count_events(start, end)
        failed = await self.repository.count_events_by_status(EventStatus.FAILED, start, end)

        return {
            "total_events": total,
            "uploads": uploads,
            "downloads": downloads,
            "deletes": deletes,
            "failed": failed,
            # Keep the original response keys for clients that already use them.
            "all_events": total,
            "upload": uploads,
            "download": downloads,
            "delete": deletes,
        }

    async def get_user_statistics(
        self, user_id: uuid.UUID, start: datetime | None = None, end: datetime | None = None
    ):
        events = await self.repository.count_events_by_users(user_id, start, end)
        uploads = await self.repository.count_events_by_type_by_user(
            EventType.UPLOAD, start, end, user_id
        )
        downloads = await self.repository.count_events_by_type_by_user(
            EventType.DOWNLOAD, start, end, user_id
        )
        deletes = await self.repository.count_events_by_type_by_user(
            EventType.DELETE, start, end, user_id
        )
        uploaded_size = await self.repository.get_uploaded_size_by_user(user_id, start, end)
        downloaded_size = await self.repository.get_download_size_by_user(user_id, start, end)

        denominator = events or 1
        return {
            "events": events,
            "upload": uploads,
            "download": downloads,
            "delete": deletes,
            "upload_percent": round(uploads / denominator * 100, 2),
            "download_percent": round(downloads / denominator * 100, 2),
            "delete_percent": round(deletes / denominator * 100, 2),
            "uploaded_size": uploaded_size,
            "downloaded_size": downloaded_size,
        }

    # Backward-compatible name used by older code.
    async def get_user_stats(self, user_id, start=None, end=None):
        return await self.get_user_statistics(user_id, start, end)

    async def get_user_stats_pro(self, user_id, start=None, end=None):
        return await self.get_user_statistics(user_id, start, end)

    async def get_bucket_statistics(
        self, bucket_name: str, start: datetime | None = None, end: datetime | None = None
    ):
        total = await self.repository.count_events_by_bucket(bucket_name, start, end)
        downloads = await self.repository.count_events_by_type_by_bucket(
            EventType.DOWNLOAD, start, end, bucket_name
        )
        uploads = await self.repository.count_events_by_type_by_bucket(
            EventType.UPLOAD, start, end, bucket_name
        )
        deletes = await self.repository.count_events_by_type_by_bucket(
            EventType.DELETE, start, end, bucket_name
        )
        return {
            "download": downloads,
            "upload": uploads,
            "delete": deletes,
            "all_events": total,
        }
