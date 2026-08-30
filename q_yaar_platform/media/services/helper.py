import logging
import uuid

from django.conf import settings
from django.db import transaction
from minio import Minio

from common.constants import AssetBucketType, AssetStatus
from common.storage import build_object_key, build_s3_client, delete_object, presign_get_url, presign_put_url
from media.api.serializers import PROFILE_CONTEXT_KEY, AssetSerializer
from media.models import Asset, AssetAskedQuestionRelation

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)

# Bucket types the upload API accepts. New buckets just need an entry here.
_SUPPORTED_BUCKETS = {AssetBucketType.GAME}

# The storage driver is stateless; this layer owns the one client for the
# process and reuses it so the underlying connection pool stays warm.
_s3_client: Minio | None = None


def _get_s3_client() -> Minio:
    """Return the process-wide S3 client, built once and reused."""
    global _s3_client
    if _s3_client is None:
        _s3_client = build_s3_client(
            endpoint=settings.S3_ENDPOINT_URL,
            access_key=settings.S3_ACCESS_KEY_ID,
            secret_key=settings.S3_SECRET_ACCESS_KEY,
            secure=settings.S3_SECURE,
            region=settings.S3_REGION,
        )
    return _s3_client


def svc_media_helper_run_validations_to_request_upload(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    bucket = request_data.get("bucket")

    if not bucket:
        return ErrorCode(ErrorCode.MISSING_BUCKET)

    if bucket not in _SUPPORTED_BUCKETS:
        return ErrorCode(ErrorCode.UNSUPPORTED_BUCKET, bucket=bucket)

    if not request_data.get("asset_name"):
        return ErrorCode(ErrorCode.MISSING_ASSET_NAME)

    return None


def svc_media_helper_validate_and_get_asset(asset_id: uuid.UUID) -> tuple:
    logger.debug(f">> ARGS: {locals()}")

    try:
        asset = Asset.objects.select_related("uploaded_by").get(external_id=asset_id, is_deleted=False)
        return None, asset
    except Asset.DoesNotExist:
        return ErrorCode(ErrorCode.INVALID_ASSET_ID, asset_id=asset_id), None


def svc_media_helper_get_assets_by_ids(asset_ids: list[str]) -> list[Asset]:
    logger.debug(f">> ARGS: {locals()}")

    ids = [str(asset_id) for asset_id in asset_ids]
    return list(Asset.objects.filter(external_id__in=ids, is_deleted=False).select_related("uploaded_by"))


def svc_media_helper_get_attachments_for_asked_question(asked_question) -> list[Asset]:
    """Return assets bound to an asked question, oldest first."""
    logger.debug(f">> ARGS: {locals()}")

    asset_ids = asked_question.asset_links.values_list("asset_id", flat=True)

    return list(
        Asset.objects.filter(pk__in=asset_ids, status=AssetStatus.UPLOADED.value, is_deleted=False).order_by("created")
    )


def svc_media_helper_get_game_for_asset(asset: Asset):
    """Return the game the asset is bound to via its asked question, or None.

    An asset is linked to a game only through AssetAskedQuestionRelation
    (exclusive binding). An unattached asset has no game, so same-game
    access cannot apply to it.
    """
    logger.debug(f">> ARGS: {locals()}")

    relation = (
        AssetAskedQuestionRelation.objects.select_related("asked_question__game_question__game")
        .filter(asset=asset)
        .first()
    )

    if relation is None:
        return None

    return relation.asked_question.game_question.game


def svc_media_helper_bind_assets(assets, asked_question) -> None:
    """Attach assets to an asked question. Caller must have validated them."""
    logger.debug(f">> ARGS: {locals()}")

    # Bind all or nothing: a failure mid-loop must roll back the whole batch
    # so the asked question never ends up with a partial attachment set.
    with transaction.atomic():
        for asset in assets:
            AssetAskedQuestionRelation.create(asset=asset, asked_question=asked_question)


# Object key layout, see Asset docstring:
#   {bucket}/{file_id}
def svc_media_helper_build_object_key(bucket: str, file_id) -> str:
    logger.debug(f">> ARGS: {locals()}")

    return build_object_key(bucket, str(file_id))


def svc_media_helper_create_asset(
    *, external_id, uploaded_by, object_key: str, asset_name: str, content_type: str
) -> Asset:
    logger.debug(f">> ARGS: {locals()}")

    return Asset.create(
        external_id=external_id,
        uploaded_by=uploaded_by,
        object_key=object_key,
        asset_name=asset_name,
        content_type=content_type,
    )


def svc_media_helper_get_serialized_assets(assets, profile, many: bool = False):
    logger.debug(f">> ARGS: {locals()}")

    # The caller's profile is the uploader for every asset (owner-scoped
    # queries upstream), so pass it via context instead of re-querying
    # per asset.
    return AssetSerializer(
        assets, many=many, context={PROFILE_CONTEXT_KEY: profile}
    ).data


def svc_media_helper_presign_put_url(object_key: str) -> tuple:
    logger.debug(f">> ARGS: {locals()}")

    upload_url = presign_put_url(_get_s3_client(), object_key)
    return upload_url, settings.S3_PRESIGN_PUT_EXPIRY


def svc_media_helper_presign_get_url(object_key: str) -> tuple:
    logger.debug(f">> ARGS: {locals()}")

    download_url = presign_get_url(_get_s3_client(), object_key)
    return download_url, settings.S3_PRESIGN_GET_EXPIRY


def svc_media_helper_presign_get_urls(assets) -> list[dict]:
    """Presign download URLs for a batch of assets.

    Presigning is local signing only (no S3 round trip), so the cost of
    N assets is N cheap crypto operations, not N network calls.
    """
    logger.debug(f">> ARGS: {locals()}")

    urls = []

    for asset in assets:
        download_url, expires_in = svc_media_helper_presign_get_url(asset.object_key)

        urls.append(
            {
                "asset_id": str(asset.external_id),
                "asset_name": asset.asset_name,
                "content_type": asset.content_type,
                "download_url": download_url,
                "expires_in": expires_in,
            }
        )

    return urls


def svc_media_helper_soft_delete(asset: Asset) -> None:
    """Mark an asset deleted without dropping the row."""
    logger.debug(f">> ARGS: {locals()}")

    asset.is_deleted = True
    asset.save()


def svc_media_helper_delete_object(object_key: str) -> None:
    """Delete the backing S3 object for an asset."""
    logger.debug(f">> ARGS: {locals()}")

    delete_object(_get_s3_client(), object_key)
