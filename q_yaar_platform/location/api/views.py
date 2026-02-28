import logging
import uuid
from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_paginated_response, get_standard_response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from location.api.serializers import LocationCreateSerializer, LocationResponseSerializer, LocationSharingSettingSerializer, WebhookTraccarLocationSerializer
from location.services.core import (
    svc_location_add_location,
    svc_location_enable_sharing,
    svc_location_get_last_locations,
    svc_location_get_locations,
    svc_location_get_current_sharing_setting,
    svc_location_reset_sharing_setting,
    svc_location_process_webhook_traccar,
)


class LocationPingsView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".LocationPingsView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def get(self, request, **kwargs):
        error, locations = svc_location_get_locations(request.query_params, serialized=False)
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
    def get(self, request, **kwargs):
        player_ids_str = request.query_params.get("player_ids")
        if not player_ids_str:
            from location.services.error_codes import ErrorCode
            return get_standard_response(ErrorCode(ErrorCode.MISSING_FILTER), None)
            
        player_ids = [pid.strip() for pid in player_ids_str.split(",") if pid.strip()]
        game_id = request.query_params.get("game_id")
        error, response = svc_location_get_last_locations(player_ids, game_id=game_id)
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


class LocationTraccarWebhookView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".LocationTraccarWebhookView")
    permission_classes = (AllowAny,)
    
    def post(self, request, **kwargs):
        serializer = WebhookTraccarLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        error, response = svc_location_process_webhook_traccar(serializer.validated_data)
        return get_standard_response(error, response)


