import logging
import uuid

from common.constants import AssetStatus, UserRolesType
from media.models import Asset

from .error_codes import ErrorCode
from .helper import (
    svc_media_helper_build_object_key,
    svc_media_helper_create_asset,
    svc_media_helper_get_serialized_assets,
    svc_media_helper_presign_get_url,
    svc_media_helper_presign_put_url,
    svc_media_helper_run_validations_to_request_upload,
    svc_media_helper_validate_and_get_asset,
    svc_media_helper_validate_and_get_game,
)

logger = logging.getLogger(__name__)


def svc_media_request_upload(request_data: dict, uploaded_by, role: UserRolesType):
    """
    Create a PENDING asset row and return a short-lived presigned PUT URL.

    The client uploads the file directly to S3 using the URL, then calls
    confirm to flip the row to UPLOADED.
    """
    logger.debug(f">> ARGS: {locals()}")

    error = svc_media_helper_run_validations_to_request_upload(request_data)
    if error:
        return error, None

    error, game = svc_media_helper_validate_and_get_game(request_data["game_id"])
    if error:
        return error, None

    file_id = uuid.uuid4()
    object_key = svc_media_helper_build_object_key(game, role, uploaded_by.external_id, file_id)

    asset = svc_media_helper_create_asset(
        uploaded_by=uploaded_by,
        role=role,
        game=game,
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


def svc_media_confirm_upload(asset_id: uuid.UUID, serialized: bool = True):
    """Mark an asset UPLOADED after the client reports a finished S3 PUT."""
    logger.debug(f">> ARGS: {locals()}")

    error, asset = svc_media_helper_validate_and_get_asset(asset_id)
    if error:
        return error, None

    if asset.status == AssetStatus.UPLOADED.value:
        return ErrorCode(ErrorCode.ASSET_ALREADY_UPLOADED, asset_id=asset_id), None

    asset.status = AssetStatus.UPLOADED.value
    asset.save()

    if serialized:
        asset = svc_media_helper_get_serialized_assets(asset, many=False)

    return ErrorCode(ErrorCode.SUCCESS), asset


def svc_media_get_download_url(asset_id: uuid.UUID):
    """Return a short-lived presigned GET URL for an UPLOADED asset."""
    logger.debug(f">> ARGS: {locals()}")

    error, asset = svc_media_helper_validate_and_get_asset(asset_id)
    if error:
        return error, None

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


def svc_media_get_assets(request_data: dict, serialized: bool = True):
    """List assets, optionally filtered by game_id."""
    logger.debug(f">> ARGS: {locals()}")

    assets = Asset.objects.all()

    game_id = request_data.get("game_id")
    if game_id:
        error, game = svc_media_helper_validate_and_get_game(game_id)
        if error:
            return error, None
        assets = assets.filter(game=game)

    if serialized:
        assets = svc_media_helper_get_serialized_assets(assets, many=True)

    return ErrorCode(ErrorCode.SUCCESS), assets


def svc_media_delete_asset(asset_id: uuid.UUID, uploaded_by):
    """Delete an asset owned by `uploaded_by`. S3 cleanup is handled by the
    post_delete signal."""
    logger.debug(f">> ARGS: {locals()}")

    error, asset = svc_media_helper_validate_and_get_asset(asset_id)
    if error:
        return error, None

    if asset.uploaded_by_id != uploaded_by.pk:
        return ErrorCode(ErrorCode.ASSET_NOT_OWNED, asset_id=asset_id), None

    asset.delete()

    return ErrorCode(ErrorCode.NO_CONTENT), None
