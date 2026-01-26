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
    MISSING_TEMPLATE = "008"
    MISSING_PLACEHOLDERS = "009"
    MISSING_QUESTION_IDS = "010"
    MISSING_GAME_ID = "011"

    # Permission Errors - 1 Series

    # Key Errors - 2 Series
    INVALID_REWARD_TYPE = "201"

    # Object Does Not Exist Errors - 3 series
    INVALID_REWARD_ID = "301"
    INVALID_CATEGORY_ID = "302"
    INVALID_QUESTION_ID = "303"
    INVALID_QUESTION_IDS = "304"

    # Integrity Errors - 4 Series

    ERROR_CODE_HTTP_MAP = {
        MISSING_REWARD_NAME: status.HTTP_400_BAD_REQUEST,
        MISSING_REWARD_TYPE: status.HTTP_400_BAD_REQUEST,
        MISSING_REWARD_META: status.HTTP_400_BAD_REQUEST,
        INVALID_REWARD_META: status.HTTP_400_BAD_REQUEST,
        MISSING_CATEGORY_NAME: status.HTTP_400_BAD_REQUEST,
        MISSING_REWARD_ID: status.HTTP_400_BAD_REQUEST,
        MISSING_PRIORITY: status.HTTP_400_BAD_REQUEST,
        MISSING_TEMPLATE: status.HTTP_400_BAD_REQUEST,
        MISSING_PLACEHOLDERS: status.HTTP_400_BAD_REQUEST,
        MISSING_QUESTION_IDS: status.HTTP_400_BAD_REQUEST,
        MISSING_GAME_ID: status.HTTP_400_BAD_REQUEST,
        INVALID_REWARD_TYPE: status.HTTP_400_BAD_REQUEST,
        INVALID_REWARD_ID: status.HTTP_400_BAD_REQUEST,
        INVALID_CATEGORY_ID: status.HTTP_400_BAD_REQUEST,
        INVALID_QUESTION_ID: status.HTTP_400_BAD_REQUEST,
        INVALID_QUESTION_IDS: status.HTTP_400_BAD_REQUEST,
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

    def get_string_for_missing_template(kwargs: dict):
        return "Missing template"

    def get_string_for_missing_placeholders(kwargs: dict):
        return "Missing placeholders"

    def get_string_for_missing_question_ids(kwargs: dict):
        return "Missing question_ids"

    def get_string_for_missing_game_id(kwargs: dict):
        return "Missing game_id"

    def get_string_for_invalid_reward_type(kwargs: dict):
        return f"Invalid reward_type: {kwargs.get('reward_type')}"

    def get_string_for_invalid_reward_id(kwargs: dict):
        return f"Invalid reward_id: {kwargs.get('reward_id')}"

    def get_string_for_invalid_category_id(kwargs: dict):
        return f"Invalid category_id: {kwargs.get('category_id')}"

    def get_string_for_invalid_question_id(kwargs: dict):
        return f"Invalid question_id: {kwargs.get('question_id')}"

    def get_string_for_invalid_question_ids(kwargs: dict):
        return f"Invalid question_ids: {kwargs.get('question_ids')}"

    CODE_MESSAGE_MAP = {
        MISSING_REWARD_NAME: get_string_for_missing_reward_name,
        MISSING_REWARD_TYPE: get_string_for_missing_reward_type,
        MISSING_REWARD_META: get_string_for_missing_reward_meta,
        INVALID_REWARD_META: get_string_for_invalid_reward_meta,
        MISSING_CATEGORY_NAME: get_string_for_missing_category_name,
        MISSING_REWARD_ID: get_string_for_missing_reward_id,
        MISSING_PRIORITY: get_string_for_missing_priority,
        MISSING_TEMPLATE: get_string_for_missing_template,
        MISSING_PLACEHOLDERS: get_string_for_missing_placeholders,
        MISSING_QUESTION_IDS: get_string_for_missing_question_ids,
        MISSING_GAME_ID: get_string_for_missing_game_id,
        INVALID_REWARD_TYPE: get_string_for_invalid_reward_type,
        INVALID_REWARD_ID: get_string_for_invalid_reward_id,
        INVALID_CATEGORY_ID: get_string_for_invalid_category_id,
        INVALID_QUESTION_ID: get_string_for_invalid_question_id,
        INVALID_QUESTION_IDS: get_string_for_invalid_question_ids,
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
