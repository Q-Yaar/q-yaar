import logging

from rest_framework import status

from common.base_error_codes import BaseErrorCode
from common.constants import ModuleErrorPrefix

logger = logging.getLogger(__name__)


class ErrorCode(BaseErrorCode):
    # Value Errors - 0 Series
    MISSING_GAME_ID = "001"
    MISSING_ASSET_NAME = "002"

    # Key Errors - 2 Series
    INVALID_GAME_ID = "201"
    INVALID_ASSET_ID = "202"

    # State Errors - 3 Series
    ASSET_NOT_UPLOADED = "301"
    ASSET_ALREADY_UPLOADED = "302"
    ASSET_NOT_OWNED = "303"
    ASSET_NOT_IN_GAME = "304"
    ASSET_ALREADY_ATTACHED = "305"

    ERROR_CODE_HTTP_MAP = {
        MISSING_GAME_ID: status.HTTP_400_BAD_REQUEST,
        MISSING_ASSET_NAME: status.HTTP_400_BAD_REQUEST,
        INVALID_GAME_ID: status.HTTP_400_BAD_REQUEST,
        INVALID_ASSET_ID: status.HTTP_400_BAD_REQUEST,
        ASSET_NOT_UPLOADED: status.HTTP_409_CONFLICT,
        ASSET_ALREADY_UPLOADED: status.HTTP_409_CONFLICT,
        ASSET_NOT_OWNED: status.HTTP_403_FORBIDDEN,
        ASSET_NOT_IN_GAME: status.HTTP_400_BAD_REQUEST,
        ASSET_ALREADY_ATTACHED: status.HTTP_409_CONFLICT,
    }

    def get_string_for_missing_game_id(kwargs: dict):
        return "Missing game_id"

    def get_string_for_missing_asset_name(kwargs: dict):
        return "Missing asset_name"

    def get_string_for_invalid_game_id(kwargs: dict):
        return f"Invalid game_id: {kwargs.get('game_id')}"

    def get_string_for_invalid_asset_id(kwargs: dict):
        return f"Invalid asset_id: {kwargs.get('asset_id')}"

    def get_string_for_asset_not_uploaded(kwargs: dict):
        return f"Asset not uploaded yet: {kwargs.get('asset_id')}"

    def get_string_for_asset_already_uploaded(kwargs: dict):
        return f"Asset already uploaded: {kwargs.get('asset_id')}"

    def get_string_for_asset_not_owned(kwargs: dict):
        return f"Asset not owned by player: {kwargs.get('asset_id')}"

    def get_string_for_asset_not_in_game(kwargs: dict):
        return f"Asset not in game: {kwargs.get('asset_id')}"

    def get_string_for_asset_already_attached(kwargs: dict):
        return f"Asset already attached to a question: {kwargs.get('asset_id')}"

    CODE_MESSAGE_MAP = {
        MISSING_GAME_ID: get_string_for_missing_game_id,
        MISSING_ASSET_NAME: get_string_for_missing_asset_name,
        INVALID_GAME_ID: get_string_for_invalid_game_id,
        INVALID_ASSET_ID: get_string_for_invalid_asset_id,
        ASSET_NOT_UPLOADED: get_string_for_asset_not_uploaded,
        ASSET_ALREADY_UPLOADED: get_string_for_asset_already_uploaded,
        ASSET_NOT_OWNED: get_string_for_asset_not_owned,
        ASSET_NOT_IN_GAME: get_string_for_asset_not_in_game,
        ASSET_ALREADY_ATTACHED: get_string_for_asset_already_attached,
    }

    def __init__(self, code, **kwargs) -> None:
        self.ERROR_CODE_HTTP_MAP.update(super().ERROR_CODE_HTTP_MAP)
        self.CODE_MESSAGE_MAP.update(super().CODE_MESSAGE_MAP)

        (
            logger.debug(f">> ARGS: {locals()}")
            if code in [self.SUCCESS, self.CREATED, self.NO_CONTENT]
            else logger.warning(f"{self.CODE_MESSAGE_MAP[code](kwargs)} - {locals()}")
        )

        super().__init__(
            code,
            self.ERROR_CODE_HTTP_MAP[code],
            self.CODE_MESSAGE_MAP[code](kwargs) if code not in [self.SUCCESS, self.CREATED, self.NO_CONTENT] else None,
            ModuleErrorPrefix.MEDIA,
        )
