import logging

from common.base_error_codes import BaseErrorCode
from common.constants import ModuleErrorPrefix
from rest_framework import status

logger = logging.getLogger(__name__)


class ErrorCode(BaseErrorCode):
    # Value Errors - 0 Series
    MISSING_LOCATION_INPUT = "001"
    MISSING_FILTER = "002"

    # Permission Errors - 1 Series

    # Key Errors - 2 Series

    # Object Does Not Exist Errors - 3 series
    LOCATION_SHARING_DISABLED = "301"

    # Integrity Errors - 4 Series

    ERROR_CODE_HTTP_MAP = {
        MISSING_LOCATION_INPUT: status.HTTP_400_BAD_REQUEST,
        MISSING_FILTER: status.HTTP_400_BAD_REQUEST,
        LOCATION_SHARING_DISABLED: status.HTTP_404_NOT_FOUND,
    }

    def get_string_for_missing_location_input(kwargs: dict):
        return "Location input array is required and must not be empty"

    def get_string_for_missing_filter(kwargs: dict):
        return "At least one filter (game_id, team_id, or player_id) must be provided"

    def get_string_for_location_sharing_disabled(kwargs: dict):
        return "Location sharing is not enabled for this player, or player not found"

    CODE_MESSAGE_MAP = {
        MISSING_LOCATION_INPUT: get_string_for_missing_location_input,
        MISSING_FILTER: get_string_for_missing_filter,
        LOCATION_SHARING_DISABLED: get_string_for_location_sharing_disabled,
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
            ModuleErrorPrefix.LOCATION,
        )
