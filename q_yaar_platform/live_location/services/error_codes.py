import logging

from common.base_error_codes import BaseErrorCode
from common.constants import ModuleErrorPrefix
from rest_framework import status

logger = logging.getLogger(__name__)


class ErrorCode(BaseErrorCode):
    # Value Errors - 0 Series

    # Permission Errors - 1 Series
    LOCATION_SHARING_DISABLED = "101"

    # Key Errors - 2 Series
    INVALID_TRACKER_CLIENT = "201"
    UNABLE_TO_PARSE_LOCATION_DATA = "202"

    # Object Does Not Exist Errors - 3 series

    # Integrity Errors - 4 Series

    ERROR_CODE_HTTP_MAP = {
        LOCATION_SHARING_DISABLED: status.HTTP_403_FORBIDDEN,
        INVALID_TRACKER_CLIENT: status.HTTP_400_BAD_REQUEST,
        UNABLE_TO_PARSE_LOCATION_DATA: status.HTTP_400_BAD_REQUEST,
    }

    def get_string_for_location_sharing_disabled(kwargs: dict):
        return "Location sharing is disabled for player"

    def get_string_for_invalid_tracker_client(kwargs: dict):
        return f"Invalid tracker client - {kwargs['tracker_client']}"

    def get_string_for_unable_to_parse_location_data(kwargs: dict):
        return f"Unable to parse location data: {kwargs['error']}"

    CODE_MESSAGE_MAP = {
        LOCATION_SHARING_DISABLED: get_string_for_location_sharing_disabled,
        INVALID_TRACKER_CLIENT: get_string_for_invalid_tracker_client,
        UNABLE_TO_PARSE_LOCATION_DATA: get_string_for_unable_to_parse_location_data,
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
            ModuleErrorPrefix.CARD_DECK,
        )
