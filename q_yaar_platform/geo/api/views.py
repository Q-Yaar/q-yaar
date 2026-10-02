import logging

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_paginated_response, get_standard_response
from geo.api.serializers import GeoFeatureSerializer
from geo.services.core import (
    svc_geo_get_feature,
    svc_geo_get_features,
    svc_geo_get_features_within,
    svc_geo_upload_feature,
)


class GeoFeaturesListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".GeoFeaturesListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER, UserRolesType.GAME_MASTER])
    def get(self, request, **kwargs):
        error, features = svc_geo_get_features(request.query_params)
        return get_paginated_response(self, error, features, GeoFeatureSerializer)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER, UserRolesType.GAME_MASTER])
    def post(self, request, **kwargs):
        error, feature = svc_geo_upload_feature(request.data, kwargs["profile"])
        return get_standard_response(error, feature)


class GeoFeatureDetailView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".GeoFeatureDetailView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER, UserRolesType.GAME_MASTER])
    def get(self, request, feature_id: int, **kwargs):
        error, response = svc_geo_get_feature(feature_id)
        return get_standard_response(error, response)


class GeoFeaturesWithinView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".GeoFeaturesWithinView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER, UserRolesType.GAME_MASTER])
    def post(self, request, **kwargs):
        error, features = svc_geo_get_features_within(request.data)
        return get_paginated_response(self, error, features, GeoFeatureSerializer)
