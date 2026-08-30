"""
Public boundary for the media module.

Other apps (e.g. qna) import `svc_media_*` functions from here and never
reach into media.services.helper directly. This keeps the asset domain
logic and the storage driver encapsulated behind one stable surface.
"""

import logging
import uuid

from common.constants import AssetStatus
from game.models import Game
from media.models import Asset
from profile_player.models import PlayerProfile

from .error_codes import ErrorCode
from .helper import (
    svc_media_helper_bind_assets,
    svc_media_helper_get_assets_by_ids,
    svc_media_helper_get_attachments_for_asked_question,
)

logger = logging.getLogger(__name__)


def svc_media_validate_assets_for_answer(
    asset_ids: list[uuid.UUID | str], player: PlayerProfile, game: Game
):
    """
    Fetch assets by external_id and validate they may be attached to an
    answer in `game` by `player`.

    Checks, per asset:
      - exists                  -> INVALID_ASSET_ID
      - status == UPLOADED      -> ASSET_NOT_UPLOADED
      - owned by player's user   -> ASSET_NOT_OWNED
      - belongs to the same game -> ASSET_NOT_IN_GAME
      - not already attached     -> ASSET_ALREADY_ATTACHED

    Returns (None, assets) on success, (error, None) on the first failure.
    """
    logger.debug(f">> ARGS: {locals()}")

    requested = [str(asset_id) for asset_id in asset_ids]

    assets = svc_media_helper_get_assets_by_ids(requested)
    found = {str(a.external_id): a for a in assets}

    missing = set(requested) - set(found)
    if missing:
        return ErrorCode(ErrorCode.INVALID_ASSET_ID, asset_id=list(missing)), None

    player_user_external_id = str(player.get_external_id())

    for asset in assets:
        if asset.status != AssetStatus.UPLOADED.value:
            return ErrorCode(ErrorCode.ASSET_NOT_UPLOADED, asset_id=asset.external_id), None

        if str(asset.uploaded_by.external_id) != player_user_external_id:
            return ErrorCode(ErrorCode.ASSET_NOT_OWNED, asset_id=asset.external_id), None

        if asset.game_id != game.pk:
            return ErrorCode(ErrorCode.ASSET_NOT_IN_GAME, asset_id=asset.external_id), None

        if asset.asked_question_id is not None:
            return ErrorCode(ErrorCode.ASSET_ALREADY_ATTACHED, asset_id=asset.external_id), None

    return None, assets


def svc_media_bind_assets_to_asked_question(assets: list[Asset], asked_question) -> None:
    """Attach validated assets to an asked question (exclusive binding)."""
    logger.debug(f">> ARGS: {locals()}")

    svc_media_helper_bind_assets(assets, asked_question)


def svc_media_get_attachments_for_asked_question(asked_question) -> list[Asset]:
    """Return UPLOADED assets bound to an asked question, oldest first."""
    logger.debug(f">> ARGS: {locals()}")

    return svc_media_helper_get_attachments_for_asked_question(asked_question)
