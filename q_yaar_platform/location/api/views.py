import logging
import uuid
from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_paginated_response, get_standard_response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from location.api.serializers import LocationCreateSerializer, LocationResponseSerializer, LocationSharingSettingSerializer
from location.services.core import (
    svc_location_add_location,
    svc_location_enable_sharing,
    svc_location_get_last_location,
    svc_location_get_locations,
    svc_location_get_current_sharing_setting,
    svc_location_reset_sharing_setting,
)


class LocationPingsView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".LocationPingsView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def get(self, request, **kwargs):
        error, locations = svc_location_get_locations(request.query_params)
        return get_paginated_response(self, error, locations, LocationResponseSerializer)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, **kwargs):
        serializer = LocationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        error, response = svc_location_add_location(kwargs["profile"], serializer.validated_data)
        return get_standard_response(error, response)


class PlayerLastLocationView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".PlayerLastLocationView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def get(self, request, player_id: uuid.UUID, **kwargs):
        error, response = svc_location_get_last_location(player_id)
        return get_standard_response(error, response)


class LocationSharingSettingView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".LocationSharingSettingView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def get(self, request, **kwargs):
        error, response = svc_location_get_current_sharing_setting(kwargs["profile"])
        return get_standard_response(error, response)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, **kwargs):
        error, response = svc_location_enable_sharing(kwargs["profile"], request.data)
        return get_standard_response(error, response)


class LocationSharingSettingResetView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".LocationSharingSettingResetView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, **kwargs):
        error, response = svc_location_reset_sharing_setting(kwargs["profile"])
        return get_standard_response(error, response)


