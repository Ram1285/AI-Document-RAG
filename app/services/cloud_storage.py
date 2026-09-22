from pathlib import Path

import boto3

from app.core.config import get_settings


def upload_file_to_s3(file_path: str, object_key: str | None = None) -> str | None:
    settings = get_settings()
    if not settings.aws_s3_bucket:
        return None

    path = Path(file_path)
    key = object_key or f"uploads/{path.name}"
    client = boto3.client("s3", region_name=settings.aws_region)
    client.upload_file(str(path), settings.aws_s3_bucket, key)
    return f"s3://{settings.aws_s3_bucket}/{key}"
