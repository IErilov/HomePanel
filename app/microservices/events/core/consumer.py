
import asyncio
import logging
import os
import socket
import uuid

from redis.asyncio import Redis
from redis.exceptions import ResponseError

from core.database import SessionLocal
from models.event import Events, EventType, EventStatus, BucketType

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

STREAM_NAME = "events:stream"
GROUP_NAME = "event-service-group"
CONSUMER_NAME = f"{socket.gethostname()}-{uuid.uuid4()}"


def parse_event(data: dict) -> Events:
    event_type = EventType[data["event_type"].upper()]
    event_status = EventStatus[data.get("status", "SUCCESS").upper()]

    bucket_type_value = data.get("bucket_type", "unknown").lower()

    try:
        bucket_type = BucketType(bucket_type_value)
    except ValueError:
        bucket_type = BucketType.UNKNOWN

    return Events(
        IP=data.get("IP") or "unknown",
        user_id=uuid.UUID(data["user_id"]) if data.get("user_id") else None,
        bucket_name=data.get("bucket_name") or data.get("bucket_id") or "unknown",
        bucket_type=bucket_type,
        event_type=event_type,
        event_status=event_status,
        object_name=data.get("object_name") or "",
        file_size=int(data.get("file_size", 0)),
    )


async def save_event(data: dict):
    event = parse_event(data)

    async with SessionLocal() as db:
        db.add(event)
        await db.commit()


async def consume_events():
    redis = Redis.from_url(
        REDIS_URL,
        decode_responses=True,
    )

    try:
        try:
            await redis.xgroup_create(
                STREAM_NAME,
                GROUP_NAME,
                id="0-0",
                mkstream=True,
            )
            logger.info("Redis Consumer Group created")
        except ResponseError as error:
            if "BUSYGROUP" not in str(error):
                raise

        logger.info("Redis Consumer started")

        while True:
            messages = await redis.xreadgroup(
                groupname=GROUP_NAME,
                consumername=CONSUMER_NAME,
                streams={STREAM_NAME: ">"},
                count=20,
                block=5000,
            )

            for stream, entries in messages:
                for message_id, data in entries:
                    try:
                        await save_event(data)

                        await redis.xack(
                            STREAM_NAME,
                            GROUP_NAME,
                            message_id,
                        )

                        logger.info("Event saved: %s", message_id)

                    except Exception:
                        logger.exception(
                            "Failed to process event %s",
                            message_id,
                        )
                        # Не подтверждаем сообщение:
                        # оно останется pending для повторной обработки.

    finally:
        await redis.aclose()
