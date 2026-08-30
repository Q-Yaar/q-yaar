import logging
import uuid

from django.conf import settings

from common.constants import UserRolesType
from common.storage import build_object_key
from common.uuid import unique_uuid4
from game.models import Game
from game.services.interfacer import svc_game_get_game_by_id
from media.api.serializers import AssetSerializer
from media.models import Asset

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


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


def svc_media_helper_get_serialized_assets(assets, many: bool = False):
    return AssetSerializer(assets, many=many).data


def svc_media_helper_presign_put_url(object_key: str) -> tuple:
    logger.debug(f">> ARGS: {locals()}")

    from common.storage import presign_put_url

    upload_url = presign_put_url(object_key)
    return upload_url, settings.S3_PRESIGN_PUT_EXPIRY


def svc_media_helper_presign_get_url(object_key: str) -> tuple:
    logger.debug(f">> ARGS: {locals()}")

    from common.storage import presign_get_url

    download_url = presign_get_url(object_key)
    return download_url, settings.S3_PRESIGN_GET_EXPIRY
