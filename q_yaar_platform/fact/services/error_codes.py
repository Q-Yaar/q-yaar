import logging

from common.base_error_codes import BaseErrorCode
from common.constants import ModuleErrorPrefix
from rest_framework import status

logger = logging.getLogger(__name__)


class ErrorCode(BaseErrorCode):
    # Value Errors - 0 Series
    MISSING_FACT_TYPE = "001"
    MISSING_FACT_INFO = "002"
    MISSING_GAME_ID = "003"
    MISSING_TEAM_ID = "004"

    # Permission Errors - 1 Series

    # Key Errors - 2 Series
    INVALID_FACT_TYPE = "201"

    # Object Does Not Exist Errors - 3 series

    # Integrity Errors - 4 Series

    ERROR_CODE_HTTP_MAP = {
        MISSING_FACT_TYPE: status.HTTP_400_BAD_REQUEST,
        MISSING_FACT_INFO: status.HTTP_400_BAD_REQUEST,
        MISSING_GAME_ID: status.HTTP_400_BAD_REQUEST,
        MISSING_TEAM_ID: status.HTTP_400_BAD_REQUEST,
        INVALID_FACT_TYPE: status.HTTP_400_BAD_REQUEST,
    }

    def get_string_for_missing_fact_type(kwargs: dict):
        return "Missing fact_type"

    def get_string_for_missing_fact_info(kwargs: dict):
        return "Missing fact_info"

    def get_string_for_missing_game_id(kwargs: dict):
        return "Missing game_id"

    def get_string_for_missing_team_id(kwargs: dict):
        return "Missing team_id"

    def get_string_for_invalid_fact_type(kwargs: dict):
        return f"Invalid fact_type: {kwargs.get('fact_type')}"

    CODE_MESSAGE_MAP = {
        MISSING_FACT_TYPE: get_string_for_missing_fact_type,
        MISSING_FACT_INFO: get_string_for_missing_fact_info,
        MISSING_GAME_ID: get_string_for_missing_game_id,
        MISSING_TEAM_ID: get_string_for_missing_team_id,
        INVALID_FACT_TYPE: get_string_for_invalid_fact_type,
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
            ModuleErrorPrefix.FACT,
        )
