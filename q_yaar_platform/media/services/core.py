import logging
import uuid

from common.constants import AssetStatus
from common.uuid import unique_uuid4
from game.services.interfacer import svc_game_verify_player_belongs_to_game
from media.models import Asset
from profile_player.models import PlayerProfile

from .error_codes import ErrorCode
from .helper import (
    svc_media_helper_build_object_key,
    svc_media_helper_create_asset,
    svc_media_helper_get_game_for_asset,
    svc_media_helper_get_serialized_assets,
    svc_media_helper_presign_get_url,
    svc_media_helper_presign_put_url,
    svc_media_helper_run_validations_to_request_upload,
    svc_media_helper_soft_delete,
    svc_media_helper_validate_and_get_asset,
)

logger = logging.getLogger(__name__)


def svc_media_request_upload(request_data: dict, profile):
    """
    Create a PENDING asset row and return a short-lived presigned PUT URL.

    The client uploads the file directly to S3 using the URL, then calls
    confirm to flip the row to UPLOADED.

    `bucket` selects the S3 key prefix. Only "game" is supported today.
    Mandatory; the client must always specify it.
    """
    logger.debug(f">> ARGS: {locals()}")

    error = svc_media_helper_run_validations_to_request_upload(request_data)
    if error:
        return error, None

    bucket = request_data["bucket"]

    uploaded_by = profile.platform_user

    file_id = unique_uuid4()
    object_key = svc_media_helper_build_object_key(bucket, file_id)

    asset = svc_media_helper_create_asset(
        external_id=unique_uuid4(),
        uploaded_by=uploaded_by,
        object_key=object_key,
        asset_name=request_data["asset_name"],
        content_type=request_data.get("content_type", ""),
    )

    upload_url, expires_in = svc_media_helper_presign_put_url(object_key)

    response = {
        "asset_id": str(asset.get_external_id()),
        "upload_url": upload_url,
        "object_key": object_key,
        "expires_in": expires_in,
    }

    return ErrorCode(ErrorCode.CREATED), response


def svc_media_confirm_upload(asset_id: uuid.UUID, profile, serialized: bool = True):
    """Mark an asset UPLOADED after the client reports a finished S3 PUT.

    Only the player who requested the upload can confirm it.
    """
    logger.debug(f">> ARGS: {locals()}")

    error, asset = svc_media_helper_validate_and_get_asset(asset_id)
    if error:
        return error, None

    if asset.uploaded_by.external_id != profile.platform_user_id:
        return ErrorCode(ErrorCode.ASSET_NOT_OWNED, asset_id=asset_id), None

    if asset.status == AssetStatus.UPLOADED.value:
        return ErrorCode(ErrorCode.ASSET_ALREADY_UPLOADED, asset_id=asset_id), None

    asset.status = AssetStatus.UPLOADED.value
    asset.save()

    if serialized:
        asset = svc_media_helper_get_serialized_assets(asset, profile, many=False)

    return ErrorCode(ErrorCode.SUCCESS), asset


def _svc_media_can_download_via_game(asset, profile) -> bool:
    """Whether a non-owner may download `asset` via same-game membership."""
    if not isinstance(profile, PlayerProfile):
        return False

    game = svc_media_helper_get_game_for_asset(asset)
    if game is None:
        return False

    return svc_game_verify_player_belongs_to_game(profile, game) is None


def svc_media_get_download_url(asset_id: uuid.UUID, profile):
    """Return a short-lived presigned GET URL for an UPLOADED asset.

    Access policy:
      - Owner: always allowed.
      - Other players: allowed only if the asset is attached to an asked
        question in a game the player belongs to.
      - Unattached assets and game masters: owner-only.
    """
    logger.debug(f">> ARGS: {locals()}")

    error, asset = svc_media_helper_validate_and_get_asset(asset_id)
    if error:
        return error, None

    if asset.uploaded_by.external_id != profile.platform_user_id and not _svc_media_can_download_via_game(
        asset, profile
    ):
        return ErrorCode(ErrorCode.ASSET_NOT_OWNED, asset_id=asset_id), None

    if asset.status != AssetStatus.UPLOADED.value:
        return ErrorCode(ErrorCode.ASSET_NOT_UPLOADED, asset_id=asset_id), None

    download_url, expires_in = svc_media_helper_presign_get_url(asset.object_key)

    response = {
        "asset_id": str(asset.get_external_id()),
        "download_url": download_url,
        "expires_in": expires_in,
        "asset_name": asset.asset_name,
        "content_type": asset.content_type,
    }

    return ErrorCode(ErrorCode.SUCCESS), response


def svc_media_get_assets(profile, serialized: bool = True):
    """List the caller's own assets."""
    logger.debug(f">> ARGS: {locals()}")

    assets = Asset.objects.filter(uploaded_by__external_id=profile.platform_user_id)

    if serialized:
        assets = svc_media_helper_get_serialized_assets(assets, profile, many=True)

    return ErrorCode(ErrorCode.SUCCESS), assets


def svc_media_delete_asset(asset_id: uuid.UUID, profile):
    """Soft-delete an asset owned by `profile`.

    Sets is_deleted=True and keeps the row. The backing S3 object is left in
    place; a separate batch job hard-deletes soft-deleted rows later, at which
    point the post_delete signal cleans up S3.
    """
    logger.debug(f">> ARGS: {locals()}")

    error, asset = svc_media_helper_validate_and_get_asset(asset_id)
    if error:
        return error, None

    if asset.uploaded_by.external_id != profile.platform_user_id:
        return ErrorCode(ErrorCode.ASSET_NOT_OWNED, asset_id=asset_id), None

    svc_media_helper_soft_delete(asset)

    return ErrorCode(ErrorCode.NO_CONTENT), None
