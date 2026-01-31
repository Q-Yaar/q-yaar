import logging

from common.base_error_codes import BaseErrorCode
from common.constants import ModuleErrorPrefix
from rest_framework import status

logger = logging.getLogger(__name__)


class ErrorCode(BaseErrorCode):
    # Value Errors - 0 Series
    MISSING_GAME_TYPE = "001"
    MISSING_NAME = "002"
    MISSING_DESCRIPTION = "003"
    MISSING_TEAM_NAME = "004"
    MISSING_PLAYER_IDS = "005"

    # Permission Errors - 1 Series
    INVALID_GAME_STATE = "101"

    # Key Errors - 2 Series
    INVALID_GAME_TYPE = "201"

    # Object Does Not Exist Errors - 3 series
    INVALID_GAME_ID = "301"
    INVALID_TEAM_ID = "302"
    PLAYER_DOES_NOT_BELONG_TO_TEAM = "303"
    PLAYER_DOES_NOT_BELONG_TO_GAME = "304"

    # Integrity Errors - 4 Series
    ERROR_CREATING_TEAM = "401"

    ERROR_CODE_HTTP_MAP = {
        MISSING_GAME_TYPE: status.HTTP_400_BAD_REQUEST,
        MISSING_NAME: status.HTTP_400_BAD_REQUEST,
        MISSING_DESCRIPTION: status.HTTP_400_BAD_REQUEST,
        MISSING_TEAM_NAME: status.HTTP_400_BAD_REQUEST,
        MISSING_PLAYER_IDS: status.HTTP_400_BAD_REQUEST,
        INVALID_GAME_STATE: status.HTTP_403_FORBIDDEN,
        INVALID_GAME_TYPE: status.HTTP_400_BAD_REQUEST,
        INVALID_GAME_ID: status.HTTP_400_BAD_REQUEST,
        INVALID_TEAM_ID: status.HTTP_400_BAD_REQUEST,
        PLAYER_DOES_NOT_BELONG_TO_TEAM: status.HTTP_400_BAD_REQUEST,
        PLAYER_DOES_NOT_BELONG_TO_GAME: status.HTTP_400_BAD_REQUEST,
        ERROR_CREATING_TEAM: status.HTTP_400_BAD_REQUEST,
    }

    def get_string_for_missing_game_type(kwargs: dict):
        return "Missing game_type"

    def get_string_for_missing_name(kwargs: dict):
        return "Missing name"

    def get_string_for_missing_description(kwargs: dict):
        return "Missing description"

    def get_string_for_missing_team_name(kwargs: dict):
        return "Missing team_name"

    def get_string_for_missing_player_ids(kwargs: dict):
        return "Missing player_ids"

    def get_string_for_invalid_game_state(kwargs: dict):
        return f"Invalid game state for operation: {kwargs.get('game_state')}"

    def get_string_for_invalid_game_type(kwargs: dict):
        return f"Invalid game_type: {kwargs.get('game_type')}"

    def get_string_for_invalid_game_id(kwargs: dict):
        return f"Invalid game ID: {kwargs.get('game_id')}"

    def get_string_for_invalid_team_id(kwargs: dict):
        return f"Invalid team ID: {kwargs.get('team_id')}"

    def get_string_for_player_does_not_belong_to_team(kwargs: dict):
        return f"Player - {kwargs.get('profile_name')} does not belong to team - {kwargs.get('team_name')}"

    def get_string_for_player_does_not_belong_to_game(kwargs: dict):
        return f"Player - {kwargs.get('profile_name')} does not belong to game - {kwargs.get('game_name')}"

    def get_string_for_error_creating_team(kwargs: dict):
        return f"Error creating team - {kwargs.get('error')}"

    CODE_MESSAGE_MAP = {
        MISSING_GAME_TYPE: get_string_for_missing_game_type,
        MISSING_NAME: get_string_for_missing_name,
        MISSING_DESCRIPTION: get_string_for_missing_description,
        MISSING_TEAM_NAME: get_string_for_missing_team_name,
        MISSING_PLAYER_IDS: get_string_for_missing_player_ids,
        INVALID_GAME_STATE: get_string_for_invalid_game_state,
        INVALID_GAME_TYPE: get_string_for_invalid_game_type,
        INVALID_GAME_ID: get_string_for_invalid_game_id,
        INVALID_TEAM_ID: get_string_for_invalid_team_id,
        PLAYER_DOES_NOT_BELONG_TO_TEAM: get_string_for_player_does_not_belong_to_team,
        PLAYER_DOES_NOT_BELONG_TO_GAME: get_string_for_player_does_not_belong_to_game,
        ERROR_CREATING_TEAM: get_string_for_error_creating_team,
    }

    def __init__(self, code, **kwargs) -> None:
        self.ERROR_CODE_HTTP_MAP.update(super(ErrorCode, self).ERROR_CODE_HTTP_MAP)
        self.CODE_MESSAGE_MAP.update(super(ErrorCode, self).CODE_MESSAGE_MAP)

        (
            logger.debug(f">> ARGS: {locals()}")
            if code in [self.SUCCESS, self.CREATED, self.NO_CONTENT]
            else logger.warning(f"{self.CODE_MESSAGE_MAP[code](kwargs)} - {locals()}")
        )

        super(ErrorCode, self).__init__(
            code,
            self.ERROR_CODE_HTTP_MAP[code],
            self.CODE_MESSAGE_MAP[code](kwargs) if code not in [self.SUCCESS, self.CREATED, self.NO_CONTENT] else None,
            ModuleErrorPrefix.GAME,
        )
