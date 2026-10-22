import logging

from rest_framework import status

from common.base_error_codes import BaseErrorCode
from common.constants import ModuleErrorPrefix

logger = logging.getLogger(__name__)


class ErrorCode(BaseErrorCode):
    # Value Errors - 0 Series
    MISSING_POLYGON = "001"
    MISSING_LATITUDE = "002"
    MISSING_LONGITUDE = "003"
    MISSING_RADIUS = "004"
    MISSING_NAME = "005"
    MISSING_GEOMETRY = "006"

    # Key Errors - 2 Series
    INVALID_FCLASS = "201"
    INVALID_POLYGON = "202"
    INVALID_LATITUDE = "203"
    INVALID_LONGITUDE = "204"
    INVALID_RADIUS = "205"
    INVALID_GEOMETRY = "206"
    INVALID_NAME = "207"
    INVALID_TAGS = "208"

    # Object Does Not Exist Errors - 3 series
    INVALID_FEATURE_ID = "301"

    # Integrity Errors - 4 Series

    ERROR_CODE_HTTP_MAP = {
        MISSING_POLYGON: status.HTTP_400_BAD_REQUEST,
        MISSING_LATITUDE: status.HTTP_400_BAD_REQUEST,
        MISSING_LONGITUDE: status.HTTP_400_BAD_REQUEST,
        MISSING_RADIUS: status.HTTP_400_BAD_REQUEST,
        MISSING_NAME: status.HTTP_400_BAD_REQUEST,
        MISSING_GEOMETRY: status.HTTP_400_BAD_REQUEST,
        INVALID_FCLASS: status.HTTP_400_BAD_REQUEST,
        INVALID_POLYGON: status.HTTP_400_BAD_REQUEST,
        INVALID_LATITUDE: status.HTTP_400_BAD_REQUEST,
        INVALID_LONGITUDE: status.HTTP_400_BAD_REQUEST,
        INVALID_RADIUS: status.HTTP_400_BAD_REQUEST,
        INVALID_GEOMETRY: status.HTTP_400_BAD_REQUEST,
        INVALID_NAME: status.HTTP_400_BAD_REQUEST,
        INVALID_TAGS: status.HTTP_400_BAD_REQUEST,
        INVALID_FEATURE_ID: status.HTTP_400_BAD_REQUEST,
    }

    def get_string_for_missing_polygon(kwargs: dict):
        return "Missing polygon"

    def get_string_for_missing_latitude(kwargs: dict):
        return "Missing lat"

    def get_string_for_missing_longitude(kwargs: dict):
        return "Missing lng"

    def get_string_for_missing_radius(kwargs: dict):
        return "Missing radius"

    def get_string_for_missing_name(kwargs: dict):
        return "Missing name"

    def get_string_for_missing_geometry(kwargs: dict):
        return "Missing geometry"

    def get_string_for_invalid_fclass(kwargs: dict):
        return f"Invalid fclass: {kwargs.get('fclass')}"

    def get_string_for_invalid_polygon(kwargs: dict):
        return f"Invalid polygon: {kwargs.get('error')}"

    def get_string_for_invalid_latitude(kwargs: dict):
        return f"Invalid lat: {kwargs.get('lat')}"

    def get_string_for_invalid_longitude(kwargs: dict):
        return f"Invalid lng: {kwargs.get('lng')}"

    def get_string_for_invalid_radius(kwargs: dict):
        return f"Invalid radius: {kwargs.get('radius')}"

    def get_string_for_invalid_geometry(kwargs: dict):
        return f"Invalid geometry: {kwargs.get('error')}"

    def get_string_for_invalid_name(kwargs: dict):
        return "Invalid name"

    def get_string_for_invalid_tags(kwargs: dict):
        return "Invalid tags"

    def get_string_for_invalid_feature_id(kwargs: dict):
        return f"Invalid feature_id: {kwargs.get('feature_id')}"

    CODE_MESSAGE_MAP = {
        MISSING_POLYGON: get_string_for_missing_polygon,
        MISSING_LATITUDE: get_string_for_missing_latitude,
        MISSING_LONGITUDE: get_string_for_missing_longitude,
        MISSING_RADIUS: get_string_for_missing_radius,
        MISSING_NAME: get_string_for_missing_name,
        MISSING_GEOMETRY: get_string_for_missing_geometry,
        INVALID_FCLASS: get_string_for_invalid_fclass,
        INVALID_POLYGON: get_string_for_invalid_polygon,
        INVALID_LATITUDE: get_string_for_invalid_latitude,
        INVALID_LONGITUDE: get_string_for_invalid_longitude,
        INVALID_RADIUS: get_string_for_invalid_radius,
        INVALID_GEOMETRY: get_string_for_invalid_geometry,
        INVALID_NAME: get_string_for_invalid_name,
        INVALID_TAGS: get_string_for_invalid_tags,
        INVALID_FEATURE_ID: get_string_for_invalid_feature_id,
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
            ModuleErrorPrefix.GEO,
        )
