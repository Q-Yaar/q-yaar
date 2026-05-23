import logging
import uuid

from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_standard_response
from live_location.services.core import svc_live_location_add_location_ping
from rest_framework import generics
from rest_framework.permissions import AllowAny


class LocationTrackingView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".LocationTrackingView")
    permission_classes = (AllowAny,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, tracker_client: str, tracking_id: uuid.UUID, **kwargs):
        error, response = svc_live_location_add_location_ping(
            tracker_client=tracker_client, tracking_id=tracking_id, request_data=request.data
        )
        return get_standard_response(error, response)
