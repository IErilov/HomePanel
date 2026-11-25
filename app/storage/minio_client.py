
import io
import re
import os
import boto3

from botocore.exceptions import ClientError
from fastapi.responses import StreamingResponse


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")


s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name="us-east-1",
)


def sanitize_bucket_name(raw_name: str) -> str:
    clean = re.sub(
        r"[^a-z0-9-]",
        "-",
        raw_name.lower(),
    ).strip("-")

    return clean[:63] if len(clean) >= 3 else f"bucket-{clean}"


def create_bucket(bucket_name: str):
    clean_name = sanitize_bucket_name(bucket_name)

    try:
        s3.head_bucket(Bucket=clean_name)

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")

        if error_code == "404":
            s3.create_bucket(Bucket=clean_name)
            print(f"Бакет '{clean_name}' успешно создан в MinIO")

        else:
            print(
                f"Ошибка MinIO при проверке/создании '{clean_name}': {e}"
            )
            raise


def upload_to_minio(file, bucket_name: str) -> bool:
    try:
        s3.upload_fileobj(
            file.file,
            sanitize_bucket_name(bucket_name),
            file.filename,
        )
        return True

    except ClientError as e:
        print(e)
        return False


def download_from_minio(filename: str, bucket_name: str):
    try:
        fileobj = io.BytesIO()

        s3.download_fileobj(
            sanitize_bucket_name(bucket_name),
            filename,
            fileobj,
        )

        fileobj.seek(0)

        return StreamingResponse(
            fileobj,
            media_type="application/octet-stream",
        )

    except ClientError as e:
        print(e)
        return None


def get_bucket_used_bytes(bucket_name: str) -> int:
    total_size = 0

    try:
        paginator = s3.get_paginator("list_objects_v2")

        for page in paginator.paginate(
            Bucket=sanitize_bucket_name(bucket_name)
        ):
            for obj in page.get("Contents", []):
                total_size += obj.get("Size", 0)

        return total_size

    except ClientError as e:
        print(f"Ошибка получения объёма бакета: {e}")
        raise


def check_upload_size(
    file_size: int,
    bucket_name: str,
    quota_bytes: int,
) -> bool:

    used_bytes = get_bucket_used_bytes(bucket_name)

    return used_bytes + file_size <= quota_bytes


def list_files(bucket_name: str) -> list[dict]:
    bucket_name = sanitize_bucket_name(bucket_name)
    files = []

    try:
        paginator = s3.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get("Contents", []):
                files.append({
                    "filename": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": (
                        obj["LastModified"].isoformat()
                        if obj.get("LastModified") else None
                    ),
                })

        return files

    except ClientError as e:
        print(f"Ошибка получения списка файлов: {e}")
        raise


def delete_file(bucket_name: str, filename: str) -> bool:
    bucket_name = sanitize_bucket_name(bucket_name)

    try:
        s3.delete_object(
            Bucket=bucket_name,
            Key=filename,
        )
        return True

    except ClientError as e:
        print(f"Ошибка удаления файла: {e}")
        return False


def rename_file(
    bucket_name: str,
    old_filename: str,
    new_filename: str,
) -> bool:

    bucket_name = sanitize_bucket_name(bucket_name)

    try:
        s3.copy_object(
            Bucket=bucket_name,
            Key=new_filename,
            CopySource={
                "Bucket": bucket_name,
                "Key": old_filename,
            },
        )

        s3.delete_object(
            Bucket=bucket_name,
            Key=old_filename,
        )

        return True

    except ClientError as e:
        print(f"Ошибка переименования файла: {e}")
        return False
