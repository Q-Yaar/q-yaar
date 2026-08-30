"""
S3-compatible object storage driver (Deuxfleurs/Garage, MinIO, AWS S3, ...).

Thin, synchronous wrapper over the minio client. This is the lowest layer:
the media service talks to it, the API layer never does.

All access goes through `get_s3_client()`, lazily configured from Django
settings. Object keys are built from parts joined by "/":

    games/{game_external_id}/{role}/{user_external_id}/{file_id}

so every object for a game lives under a single, export-friendly prefix.
"""

import logging
from datetime import timedelta
from urllib.parse import urlparse

from django.conf import settings
from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)

_client: Minio | None = None


def get_s3_client() -> Minio:
    """Return a process-wide Minio client configured from settings."""
    global _client
    if _client is not None:
        return _client

    # minio expects a bare host:port (no scheme); strip it from the endpoint URL.
    parsed = urlparse(settings.S3_ENDPOINT_URL)
    endpoint = parsed.netloc or settings.S3_ENDPOINT_URL

    _client = Minio(
        endpoint,
        access_key=settings.S3_ACCESS_KEY_ID,
        secret_key=settings.S3_SECRET_ACCESS_KEY,
        secure=settings.S3_SECURE,
        region=settings.S3_REGION,
    )
    return _client


def build_object_key(*parts: str) -> str:
    """Join `parts` into a forward-slash-separated object key."""
    return "/".join(part.strip("/") for part in parts)


def presign_put_url(object_key: str, expires: int | None = None) -> str:
    """Return a short-lived presigned PUT URL for `object_key`."""
    client = get_s3_client()
    expiry = timedelta(seconds=expires if expires is not None else settings.S3_PRESIGN_PUT_EXPIRY)
    return client.presigned_put_object(settings.S3_BUCKET_NAME, object_key, expires=expiry)


def presign_get_url(object_key: str, expires: int | None = None) -> str:
    """Return a short-lived presigned GET URL for `object_key`."""
    client = get_s3_client()
    expiry = timedelta(seconds=expires if expires is not None else settings.S3_PRESIGN_GET_EXPIRY)
    return client.presigned_get_object(settings.S3_BUCKET_NAME, object_key, expires=expiry)


def object_exists(object_key: str) -> bool:
    """Return True if `object_key` exists in the bucket."""
    client = get_s3_client()
    try:
        client.stat_object(settings.S3_BUCKET_NAME, object_key)
        return True
    except S3Error as e:
        # NoSuchKey / 404
        logger.debug(f"object_exists miss for {object_key}: {e}")
        return False
