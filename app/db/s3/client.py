"""S3 client for storing artifacts (charts, reports)."""

import boto3
from botocore.exceptions import ClientError
from app.config import settings
from loguru import logger
from typing import Optional

_s3_client = None


def get_s3_client():
    """Get or create S3 client."""
    global _s3_client

    if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
        logger.warning("S3 credentials not configured")
        return None

    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        logger.info("Created S3 client")

    return _s3_client


async def upload_file(file_path: str, object_name: str) -> Optional[str]:
    """
    Upload file to S3 bucket.

    Args:
        file_path: Local file path
        object_name: S3 object name/key

    Returns:
        S3 URL if successful, None otherwise
    """
    client = get_s3_client()
    if not client:
        return None

    try:
        client.upload_file(file_path, settings.S3_BUCKET_NAME, object_name)
        url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{object_name}"
        logger.info(f"Uploaded {object_name} to S3")
        return url
    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        return None


async def upload_bytes(data: bytes, object_name: str, content_type: str = "application/octet-stream") -> Optional[str]:
    """
    Upload bytes to S3 bucket.

    Args:
        data: Bytes to upload
        object_name: S3 object name/key
        content_type: MIME type

    Returns:
        S3 URL if successful, None otherwise
    """
    client = get_s3_client()
    if not client:
        return None

    try:
        client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=object_name,
            Body=data,
            ContentType=content_type,
        )
        url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{object_name}"
        logger.info(f"Uploaded {object_name} to S3")
        return url
    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        return None


async def get_presigned_url(object_name: str, expiration: int = 3600) -> Optional[str]:
    """
    Generate presigned URL for S3 object.

    Args:
        object_name: S3 object key
        expiration: URL expiration in seconds

    Returns:
        Presigned URL or None
    """
    client = get_s3_client()
    if not client:
        return None

    try:
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": object_name},
            ExpiresIn=expiration,
        )
        return url
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        return None
