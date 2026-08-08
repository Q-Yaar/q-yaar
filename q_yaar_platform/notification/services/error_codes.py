import logging

from common.base_error_codes import BaseErrorCode
from common.constants import ModuleErrorPrefix
from rest_framework import status

logger = logging.getLogger(__name__)


class ErrorCode(BaseErrorCode):
    # Value Errors - 0 Series
    MISSING_ENDPOINT = "001"
    MISSING_KEYS = "002"
    MISSING_P256DH = "003"
    MISSING_AUTH = "004"

    # Permission Errors - 1 Series
    # Key Errors - 2 Series

    # Object Does Not Exist Errors - 3 series
    INVALID_NOTIFICATION_ID = "301"

    # Integrity Errors - 4 Series

    ERROR_CODE_HTTP_MAP = {
        MISSING_ENDPOINT: status.HTTP_400_BAD_REQUEST,
        MISSING_KEYS: status.HTTP_400_BAD_REQUEST,
        MISSING_P256DH: status.HTTP_400_BAD_REQUEST,
        MISSING_AUTH: status.HTTP_400_BAD_REQUEST,
        INVALID_NOTIFICATION_ID: status.HTTP_400_BAD_REQUEST,
    }

    def get_string_for_missing_endpoint(kwargs: dict):
        return "Missing endpoint"

    def get_string_for_missing_keys(kwargs: dict):
        return "Missing keys"

    def get_string_for_missing_p256dh(kwargs: dict):
        return "Missing keys.p256dh"

    def get_string_for_missing_auth(kwargs: dict):
        return "Missing keys.auth"

    def get_string_for_invalid_notification_id(kwargs: dict):
        return f"Invalid notification id - {kwargs['notification_id']}"

    CODE_MESSAGE_MAP = {
        MISSING_ENDPOINT: get_string_for_missing_endpoint,
        MISSING_KEYS: get_string_for_missing_keys,
        MISSING_P256DH: get_string_for_missing_p256dh,
        MISSING_AUTH: get_string_for_missing_auth,
        INVALID_NOTIFICATION_ID: get_string_for_invalid_notification_id,
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
