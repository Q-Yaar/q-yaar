"""
S3-compatible object storage driver (Deuxfleurs/Garage, MinIO, AWS S3, ...).

Thin, synchronous wrapper over the minio client. This is the lowest layer:
the media service talks to it, the API layer never does.

This module is stateless: `build_s3_client()` constructs a fresh client from
explicit config and caches nothing — the driver never reads Django settings,
so any caller passes its full S3 config. Callers own the returned client and
reuse it across operations to keep the underlying connection pool warm.
Object keys are built from parts joined by "/":

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


def build_s3_client(
    *,
    endpoint: str,
    access_key: str,
    secret_key: str,
    secure: bool,
    region: str,
) -> Minio:
    """Build and return a new Minio client from explicit S3 config.

    All args are required: the driver reads no settings itself, so any
    consumer must pass its full config. Pure factory; no caching is done
    here. Callers should hold onto the returned client and reuse it to keep
    the underlying connection pool warm.
    """
    return Minio(
        _bare_endpoint(endpoint),
        access_key=access_key,
        secret_key=secret_key,
        secure=secure,
        region=region,
    )


def _bare_endpoint(endpoint: str) -> str:
    """minio expects a bare host:port (no scheme); strip it if present."""
    parsed = urlparse(endpoint)
    return parsed.netloc or endpoint


def build_object_key(*parts: str) -> str:
    """Join `parts` into a forward-slash-separated object key."""
    return "/".join(part.strip("/") for part in parts)


def presign_put_url(client: Minio, object_key: str, expires: int | None = None) -> str:
    """Return a short-lived presigned PUT URL for `object_key`."""
    expiry = timedelta(seconds=expires if expires is not None else settings.S3_PRESIGN_PUT_EXPIRY)
    return client.presigned_put_object(settings.S3_BUCKET_NAME, object_key, expires=expiry)


def presign_get_url(client: Minio, object_key: str, expires: int | None = None) -> str:
    """Return a short-lived presigned GET URL for `object_key`."""
    expiry = timedelta(seconds=expires if expires is not None else settings.S3_PRESIGN_GET_EXPIRY)
    return client.presigned_get_object(settings.S3_BUCKET_NAME, object_key, expires=expiry)


def object_exists(client: Minio, object_key: str) -> bool:
    """Return True if `object_key` exists in the bucket."""
    try:
        client.stat_object(settings.S3_BUCKET_NAME, object_key)
        return True
    except S3Error as e:
        # NoSuchKey / 404
        logger.debug(f"object_exists miss for {object_key}: {e}")
        return False
