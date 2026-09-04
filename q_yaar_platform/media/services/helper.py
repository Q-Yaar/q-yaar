import logging
import uuid

from django.conf import settings
from minio import Minio

from common.constants import AssetStatus, UserRolesType
from common.storage import build_object_key, build_s3_client, delete_object, presign_get_url, presign_put_url
from common.uuid import unique_uuid4
from game.models import Game
from game.services.interfacer import svc_game_get_game_by_id
from media.api.serializers import AssetSerializer
from media.models import Asset
from profile_game_master.services.interfacer import svc_game_master_get_game_master_for_platform_user
from profile_player.services.interfacer import svc_player_get_player_for_platform_user

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)

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

    if not request_data.get("game_id"):
        return ErrorCode(ErrorCode.MISSING_GAME_ID)

    if not request_data.get("asset_name"):
        return ErrorCode(ErrorCode.MISSING_ASSET_NAME)

    return None


def svc_media_helper_validate_and_get_game(game_id) -> tuple:
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_get_game_by_id(game_id)


def svc_media_helper_validate_and_get_asset(asset_id: uuid.UUID) -> tuple:
    logger.debug(f">> ARGS: {locals()}")

    try:
        asset = Asset.objects.get(external_id=asset_id)
        return None, asset
    except Asset.DoesNotExist:
        return ErrorCode(ErrorCode.INVALID_ASSET_ID, asset_id=asset_id), None


def svc_media_helper_get_assets_by_ids(asset_ids) -> list[Asset]:
    logger.debug(f">> ARGS: {locals()}")

    ids = [str(asset_id) for asset_id in asset_ids]
    return list(Asset.objects.filter(external_id__in=ids).select_related("uploaded_by", "game"))


def svc_media_helper_get_attachments_for_asked_question(asked_question) -> list[Asset]:
    """Return assets bound to an asked question, oldest first."""
    logger.debug(f">> ARGS: {locals()}")

    return list(asked_question.attachments.filter(status=AssetStatus.UPLOADED.value).order_by("created"))


def svc_media_helper_bind_assets(assets, asked_question) -> None:
    """Attach assets to an asked question. Caller must have validated them."""
    logger.debug(f">> ARGS: {locals()}")

    asset_pks = [asset.pk for asset in assets]
    Asset.objects.filter(pk__in=asset_pks).update(asked_question=asked_question)


# Object key layout, see Asset docstring:
#   games/{game_external_id}/{role}/{user_external_id}/{file_id}
def svc_media_helper_build_object_key(game: Game, role: UserRolesType, user_external_id, file_id) -> str:
    logger.debug(f">> ARGS: {locals()}")

    return build_object_key(
        "games",
        str(game.external_id),
        UserRolesType.get_string_for_type(role),
        str(user_external_id),
        str(file_id),
    )


def svc_media_helper_create_asset(
    *, uploaded_by, role: UserRolesType, game: Game, object_key: str, asset_name: str, content_type: str
) -> Asset:
    logger.debug(f">> ARGS: {locals()}")

    return Asset.create(
        external_id=unique_uuid4(),
        uploaded_by=uploaded_by,
        role=role,
        game=game,
        object_key=object_key,
        asset_name=asset_name,
        content_type=content_type,
    )


# Role -> profile service lookup. Resolves the uploader's profile so the
# serializer can return it instead of a bare role string.
_PROFILE_GETTERS = {
    UserRolesType.PLAYER: svc_player_get_player_for_platform_user,
    UserRolesType.GAME_MASTER: svc_game_master_get_game_master_for_platform_user,
}


def _resolve_uploader_profile(asset: Asset) -> None:
    """Fetch the uploader's profile and stash it on the asset for the serializer."""
    getter = _PROFILE_GETTERS[UserRolesType(asset.role)]
    _, profile = getter(asset.uploaded_by)
    asset._uploader_profile = profile


def svc_media_helper_get_serialized_assets(assets, many: bool = False):
    logger.debug(f">> ARGS: {locals()}")

    if many:
        for asset in assets:
            _resolve_uploader_profile(asset)
    else:
        _resolve_uploader_profile(assets)

    return AssetSerializer(assets, many=many).data


def svc_media_helper_presign_put_url(object_key: str) -> tuple:
    logger.debug(f">> ARGS: {locals()}")

    upload_url = presign_put_url(_get_s3_client(), object_key)
    return upload_url, settings.S3_PRESIGN_PUT_EXPIRY


def svc_media_helper_presign_get_url(object_key: str) -> tuple:
    logger.debug(f">> ARGS: {locals()}")

    download_url = presign_get_url(_get_s3_client(), object_key)
    return download_url, settings.S3_PRESIGN_GET_EXPIRY


def svc_media_helper_delete_object(object_key: str) -> None:
    """Delete the backing S3 object for an asset."""
    logger.debug(f">> ARGS: {locals()}")

    delete_object(_get_s3_client(), object_key)
