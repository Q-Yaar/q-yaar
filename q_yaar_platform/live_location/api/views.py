import logging
import uuid

from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_standard_response
from live_location.services.core import (
    svc_live_location_delete_location_settings,
    svc_live_location_enable_location_sharing,
    svc_live_location_get_last_locations,
    svc_live_location_get_location_settings,
)
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class LastLocationListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".LastLocationListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def get(self, request, game_id: uuid.UUID, **kwargs):
        error, response = svc_live_location_get_last_locations(game_id=game_id)
        return get_standard_response(error, response)


class LocationSettingsView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".LocationSettingsView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def get(self, request, **kwargs):
        error, response = svc_live_location_get_location_settings(player=kwargs["profile"])
        return get_standard_response(error, response)

    # To reset the tracking code
    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def delete(self, request, **kwargs):
        error, response = svc_live_location_delete_location_settings(player=kwargs["profile"])
        return get_standard_response(error, response)


class LocationSharingEnableView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".LocationSharingEnableView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, **kwargs):
        error, response = svc_live_location_enable_location_sharing(player=kwargs["profile"], enabled=True)
        return get_standard_response(error, response)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def delete(self, request, **kwargs):
        error, response = svc_live_location_enable_location_sharing(player=kwargs["profile"], enabled=False)
        return get_standard_response(error, response)
