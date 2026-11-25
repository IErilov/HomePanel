
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from microservices.events.publisher import publish_event
from pydantic import BaseModel, Field
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models.bucket import Buckets, BucketType
from db.models.user import User, AccountType

from core.user.getters import get_current_user, get_optional_user

from microservices.redis.services.rate_limit import rate_limit_for_bucket
from storage.minio_client import (
    create_bucket,
    upload_to_minio,
    download_from_minio,
    list_files,
    delete_file,
    rename_file,
    check_upload_size,
)

router = APIRouter(
    prefix="/api/buckets",
    tags=["Buckets & Storage"],
)


class RenameFileRequest(BaseModel):
    new_filename: str = Field(min_length=1, max_length=1024)


async def get_bucket_or_404(
    bucket_id: uuid.UUID,
    db: AsyncSession,
) -> Buckets:
    result = await db.execute(
        select(Buckets).where(Buckets.id == bucket_id)
    )

    bucket = result.scalar_one_or_none()

    if not bucket:
        raise HTTPException(
            status_code=404,
            detail="Бакет не найден",
        )

    return bucket


async def publish_storage_event(
    event_type: str,
    user_id: str | None,
    bucket_id: str,
    object_name: str | None = None,
    file_size: int = 0,
):
    try:
        await publish_event(
            event_type=event_type,
            user_id=user_id,
            bucket_id=bucket_id,
            object_name=object_name,
            file_size=file_size,
            status="SUCCESS",
        )
    except Exception as e:
        print(f"Event publishing failed: {e}")


@router.get("/")
async def get_user_buckets(
    current_user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user is None:
        query = select(Buckets).where(
            Buckets.bucket_type == BucketType.OPEN
        )
    else:
        query = select(Buckets).where(
            or_(
                Buckets.bucket_type == BucketType.OPEN,
                and_(
                    Buckets.bucket_type == BucketType.PERSONAL,
                    Buckets.owner_id == current_user.id,
                ),
            )
        )

    result = await db.execute(query)
    buckets = result.scalars().all()

    return {
        "buckets": [
            {
                "id": str(bucket.id),
                "name": bucket.name,
                "bucket_type": bucket.bucket_type.value,
            }
            for bucket in buckets
        ]
    }


def check_read_access(
    bucket: Buckets,
    current_user: User | None,
):
    if bucket.bucket_type == BucketType.OPEN:
        return

    if current_user is None:
        raise HTTPException(
            status_code=401,
            detail="Требуется авторизация",
        )

    if bucket.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Нет доступа к бакету",
        )


def check_write_access(
    bucket: Buckets,
    current_user: User | None,
):
    if bucket.bucket_type == BucketType.OPEN:
        return

    if current_user is None:
        raise HTTPException(
            status_code=401,
            detail="Требуется авторизация",
        )

    if bucket.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Нет прав на загрузку",
        )


def check_manage_access(
    bucket: Buckets,
    current_user: User,
):
    if bucket.bucket_type == BucketType.OPEN:
        if current_user.account_type != AccountType.SUPER_USER:
            raise HTTPException(
                status_code=403,
                detail="Только администратор может изменять OPEN",
            )
        return

    if bucket.bucket_type == BucketType.PERSONAL:
        if bucket.owner_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Нет прав на изменение этого бакета",
            )
        return

    raise HTTPException(
        status_code=403,
        detail="Операция недоступна для этого типа бакета",
    )


@router.post("/", dependencies=[Depends(rate_limit_for_bucket())])
async def create_user_bucket(
    name: str,
    bucket_type: BucketType,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if bucket_type == BucketType.OPEN:
        if current_user.account_type != AccountType.SUPER_USER:
            raise HTTPException(
                status_code=403,
                detail="Только администратор может создавать OPEN",
            )
        owner_id = None
    else:
        owner_id = current_user.id

    bucket = Buckets(
        name=name,
        bucket_type=bucket_type,
        owner_id=owner_id,
    )

    db.add(bucket)
    await db.flush()

    try:
        create_bucket(bucket.s3_name)
        await db.commit()
        await db.refresh(bucket)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Ошибка создания бакета",
        )

    return {
        "id": str(bucket.id),
        "name": bucket.name,
        "bucket_type": bucket.bucket_type.value,
        "s3_name": bucket.s3_name,
    }


@router.post("/{bucket_id}/upload")
async def upload_file(
    bucket_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="У файла отсутствует имя",
        )

    bucket = await get_bucket_or_404(bucket_id, db)

    check_write_access(bucket, current_user)

    file_size = file.size

    if file_size is None:
        file_size = 0

        while chunk := await file.read(1024 * 1024):
            file_size += len(chunk)

        await file.seek(0)

    if not check_upload_size(
        file_size,
        bucket.s3_name,
        bucket.quota_bytes,
    ):
        raise HTTPException(
            status_code=413,
            detail="Превышена квота хранилища",
        )

    success = upload_to_minio(file, bucket.s3_name)

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Ошибка загрузки в MinIO",
        )

    await publish_storage_event(
        event_type="UPLOAD",
        user_id=str(current_user.id) if current_user else None,
        bucket_id=str(bucket.id),
        object_name=file.filename,
        file_size=file_size,
    )

    return {
        "filename": file.filename,
        "bucket": bucket.name,
        "bucket_id": str(bucket.id),
        "file_size": file_size,
    }


@router.get("/{bucket_id}/files")
async def get_bucket_files(
    bucket_id: uuid.UUID,
    current_user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    bucket = await get_bucket_or_404(bucket_id, db)
    check_read_access(bucket, current_user)

    try:
        files = list_files(bucket.s3_name)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Ошибка получения списка файлов",
        )

    return {
        "bucket_id": str(bucket.id),
        "bucket_name": bucket.name,
        "bucket_type": bucket.bucket_type.value,
        "files": files,
    }


@router.get("/{bucket_id}/download/{filename:path}")
async def download_file(
    bucket_id: uuid.UUID,
    filename: str,
    current_user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    bucket = await get_bucket_or_404(bucket_id, db)
    check_read_access(bucket, current_user)

    file_stream = download_from_minio(
        filename,
        bucket.s3_name,
    )

    if not file_stream:
        raise HTTPException(
            status_code=404,
            detail="Файл не найден",
        )

    await publish_storage_event(
        event_type="DOWNLOAD",
        user_id=str(current_user.id) if current_user else None,
        bucket_id=str(bucket.id),
        object_name=filename,
    )

    return file_stream


@router.delete("/{bucket_id}/files/{filename:path}")
async def remove_bucket_file(
    bucket_id: uuid.UUID,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bucket = await get_bucket_or_404(bucket_id, db)
    check_manage_access(bucket, current_user)

    success = delete_file(
        bucket.s3_name,
        filename,
    )

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Ошибка удаления файла",
        )

    await publish_storage_event(
        event_type="DELETE",
        user_id=str(current_user.id),
        bucket_id=str(bucket.id),
        object_name=filename,
    )

    return {
        "message": "Файл удалён",
        "filename": filename,
    }


@router.patch(
    "/{bucket_id}/files/{filename:path}",
    dependencies=[Depends(rate_limit_for_bucket())],
)
async def rename_bucket_file(
    bucket_id: uuid.UUID,
    filename: str,
    data: RenameFileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bucket = await get_bucket_or_404(bucket_id, db)
    check_manage_access(bucket, current_user)

    new_filename = data.new_filename.strip()

    if (
        not new_filename
        or new_filename == filename
        or new_filename.startswith("/")
        or "\x00" in new_filename
    ):
        raise HTTPException(
            status_code=400,
            detail="Некорректное новое имя файла",
        )

    success = rename_file(
        bucket.s3_name,
        filename,
        new_filename,
    )

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Ошибка переименования файла",
        )

    await publish_storage_event(
        event_type="RENAME",
        user_id=str(current_user.id),
        bucket_id=str(bucket.id),
        object_name=new_filename,
    )

    return {
        "message": "Файл переименован",
        "old_filename": filename,
        "new_filename": new_filename,
    }
