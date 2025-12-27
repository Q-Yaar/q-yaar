import logging

from common.base_error_codes import BaseErrorCode
from common.constants import ModuleErrorPrefix
from rest_framework import status

logger = logging.getLogger(__name__)


class ErrorCode(BaseErrorCode):
    # Value Errors - 0 Series
    MISSING_REWARD_NAME = "001"
    MISSING_REWARD_TYPE = "002"
    MISSING_REWARD_META = "003"
    INVALID_REWARD_META = "004"
    MISSING_CATEGORY_NAME = "005"
    MISSING_REWARD_ID = "006"
    MISSING_PRIORITY = "007"

    # Permission Errors - 1 Series

    # Key Errors - 2 Series
    INVALID_REWARD_TYPE = "201"

    # Object Does Not Exist Errors - 3 series
    INVALID_REWARD_ID = "301"

    # Integrity Errors - 4 Series

    ERROR_CODE_HTTP_MAP = {
        MISSING_REWARD_NAME: status.HTTP_400_BAD_REQUEST,
        MISSING_REWARD_TYPE: status.HTTP_400_BAD_REQUEST,
        MISSING_REWARD_META: status.HTTP_400_BAD_REQUEST,
        INVALID_REWARD_META: status.HTTP_400_BAD_REQUEST,
        MISSING_CATEGORY_NAME: status.HTTP_400_BAD_REQUEST,
        MISSING_REWARD_ID: status.HTTP_400_BAD_REQUEST,
        MISSING_PRIORITY: status.HTTP_400_BAD_REQUEST,
        INVALID_REWARD_TYPE: status.HTTP_400_BAD_REQUEST,
        INVALID_REWARD_ID: status.HTTP_400_BAD_REQUEST,
    }

    def get_string_for_missing_reward_name(kwargs: dict):
        return "Missing reward_name"

    def get_string_for_missing_reward_type(kwargs: dict):
        return "Missing reward_type"

    def get_string_for_missing_reward_meta(kwargs: dict):
        return "Missing reward_meta"

    def get_string_for_invalid_reward_meta(kwargs: dict):
        return f"Invalid reward_meta: {kwargs.get('reward_meta')}"

    def get_string_for_missing_category_name(kwargs: dict):
        return "Missing category_name"

    def get_string_for_missing_reward_id(kwargs: dict):
        return "Missing reward_id"

    def get_string_for_missing_priority(kwargs: dict):
        return "Missing priority"

    def get_string_for_invalid_reward_type(kwargs: dict):
        return f"Invalid reward_type: {kwargs.get('reward_type')}"

    def get_string_for_invalid_reward_id(kwargs: dict):
        return f"Invalid reward_id: {kwargs.get('reward_id')}"

    CODE_MESSAGE_MAP = {
        MISSING_REWARD_NAME: get_string_for_missing_reward_name,
        MISSING_REWARD_TYPE: get_string_for_missing_reward_type,
        MISSING_REWARD_META: get_string_for_missing_reward_meta,
        INVALID_REWARD_META: get_string_for_invalid_reward_meta,
        MISSING_CATEGORY_NAME: get_string_for_missing_category_name,
        MISSING_REWARD_ID: get_string_for_missing_reward_id,
        MISSING_PRIORITY: get_string_for_missing_priority,
        INVALID_REWARD_TYPE: get_string_for_invalid_reward_type,
        INVALID_REWARD_ID: get_string_for_invalid_reward_id,
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
            ModuleErrorPrefix.QNA,
        )
