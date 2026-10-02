import logging

from geo.services.helper import (
    svc_geo_helper_create_uploaded_feature,
    svc_geo_helper_get_fclasses,
    svc_geo_helper_get_feature_by_id,
    svc_geo_helper_get_features,
    svc_geo_helper_get_features_within,
    svc_geo_helper_get_serialized_features,
    svc_geo_helper_parse_polygon,
)

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


def svc_geo_get_features(request_data: dict, serialized: bool = False):
    """request_data = request.query_params. Optional: fclass=park,playground"""

    logger.debug(f">> ARGS: {locals()}")

    error, fclasses = svc_geo_helper_get_fclasses(request_data.get("fclass"), csv=True)
    if error:
        return error, None

    features = svc_geo_helper_get_features(fclasses)

    if serialized:
        features = svc_geo_helper_get_serialized_features(features, many=True)

    return ErrorCode(ErrorCode.SUCCESS), features


def svc_geo_get_feature(feature_id: int, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, feature = svc_geo_helper_get_feature_by_id(feature_id)
    if error:
        return error, None

    if serialized:
        feature = svc_geo_helper_get_serialized_features(feature, many=False, detail=True)

    return ErrorCode(ErrorCode.SUCCESS), feature


def svc_geo_upload_feature(request_data: dict, profile):
    """Store one user-uploaded feature. Body: {"name", "fclass",
    "geometry": {GeoJSON geometry}, "tags": {optional}}"""

    logger.debug(f">> ARGS: {locals()}")

    error, feature = svc_geo_helper_create_uploaded_feature(request_data, profile.platform_user)
    if error:
        return error, None

    return ErrorCode(ErrorCode.CREATED), svc_geo_helper_get_serialized_features(feature, many=False, detail=True)


def svc_geo_get_features_within(request_data: dict, serialized: bool = False):
    """Body: {"fclass": ["park", ...], "polygon": {GeoJSON geometry}}"""

    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("polygon"):
        return ErrorCode(ErrorCode.MISSING_POLYGON), None

    error, polygon = svc_geo_helper_parse_polygon(request_data["polygon"])
    if error:
        return error, None

    error, fclasses = svc_geo_helper_get_fclasses(request_data.get("fclass"))
    if error:
        return error, None

    features = svc_geo_helper_get_features_within(polygon, fclasses)

    if serialized:
        features = svc_geo_helper_get_serialized_features(features, many=True)

    return ErrorCode(ErrorCode.SUCCESS), features
