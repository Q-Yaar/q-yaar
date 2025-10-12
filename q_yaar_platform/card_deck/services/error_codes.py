import logging

from common.base_error_codes import BaseErrorCode
from common.constants import ModuleErrorPrefix
from rest_framework import status

logger = logging.getLogger(__name__)


class ErrorCode(BaseErrorCode):
    # Value Errors - 0 Series
    MISSING_TAG_NAME = "001"
    MISSING_MANDATORY_FIELD = "002"
    INVALID_FIELD_TYPE = "003"
    INVALID_FIELD_NAME = "004"

    # Permission Errors - 1 Series

    # Key Errors - 2 Series

    # Object Does Not Exist Errors - 3 series

    # Integrity Errors - 4 Series

    ERROR_CODE_HTTP_MAP = {
        MISSING_TAG_NAME: status.HTTP_400_BAD_REQUEST,
        MISSING_MANDATORY_FIELD: status.HTTP_400_BAD_REQUEST,
        INVALID_FIELD_TYPE: status.HTTP_400_BAD_REQUEST,
        INVALID_FIELD_NAME: status.HTTP_400_BAD_REQUEST,
    }

    def get_string_for_missing_tag_name(kwargs: dict):
        return "Missing tag_name"

    def get_string_for_missing_mandatory_field(kwargs: dict):
        index = kwargs.get("index")
        missing_fields = kwargs.get("missing_fields", [])
        return f"Card at index {index} is missing mandatory fields: {', '.join(missing_fields)}"

    def get_string_for_invalid_field_type(kwargs: dict):
        index = kwargs.get("index")
        field_name = kwargs.get("field_name")
        expected_type = kwargs.get("expected_type")
        return (
            f"Card at index {index} has invalid type for field '{field_name}'. Expected type: {expected_type.__name__}"
        )

    def get_string_for_invalid_field_name(kwargs: dict):
        index = kwargs.get("index")
        field_name = kwargs.get("field_name")
        return f"Card at index {index} has invalid field name: '{field_name}'"

    CODE_MESSAGE_MAP = {
        MISSING_TAG_NAME: get_string_for_missing_tag_name,
        MISSING_MANDATORY_FIELD: get_string_for_missing_mandatory_field,
        INVALID_FIELD_TYPE: get_string_for_invalid_field_type,
        INVALID_FIELD_NAME: get_string_for_invalid_field_name,
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
