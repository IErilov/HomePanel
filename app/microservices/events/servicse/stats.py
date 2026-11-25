from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import uuid

from repo.event import EventRepository
from models.event import EventType
from datetime import datetime

class Stats:
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

    async def get_user_stats_pro(self, user_id: uuid, start: datetime, end: datetime):
            download = await self.repository.count_events_by_type_by_user(EventType.DOWNLOAD, start, end, user_id)
            upload = await self.repository.count_events_by_type_by_user(EventType.UPLOAD, start, end, user_id)
            delete = await self.repository.count_events_by_type_by_user(EventType.DELETE, start, end, user_id)

            all_events = await self.repository.count_events_by_users(user_id, start, end )
            one = all_events/100

            downloadREit = one * download
            uploadREit = one * upload
            deleteREit = one * delete

            return  {
                        "download %": downloadREit,
                        "upload %": uploadREit,
                        "delete %": deleteREit,
                    }


    
    async def get_user_stats(self, user_id: uuid, start: datetime, end: datetime):
            events = await self.repository.count_events_by_users(user_id, start, end)
            upload = await self.repository.get_uploaded_size_by_user(user_id, start, end)
            download = await self.repository.get_download_size_by_user(user_id, start, end)
            delete = await self.repository.count_events_by_type_by_user(user_id, start, end, )

            return {
                        "events": events,
                        "download": download,
                        "upload": upload,
                        "delete": delete,
                    }

    async def get_bucket_statistics(self, bucket_name: str, start: datetime, end: datetime):
        all_events = await self.repository.count_events_by_bucket(bucket_name, start, end)
        download = await self.repository.count_events_by_type_by_bucket(EventType.DOWNLOAD, start, end)
        upload = await self.repository.count_events_by_type_by_bucket(EventType.UPLOAD, start, end)
        delete = await self.repository.count_events_by_type_by_bucket(EventType.DELETE, start, end)

        return {
                "download": download,
                "upload": upload,
                "delete": delete,
                "all_events": all_events
                }