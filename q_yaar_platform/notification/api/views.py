import logging
import uuid

from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_paginated_response, get_standard_response
from notification.api.serializers import NotificationSerializer
from notification.services.core import (
    svc_notification_get_notifications,
    svc_notification_mark_notification_read,
    svc_notification_subscribe,
)
from rest_framework import generics

logger = logging.getLogger(__name__)


class WebPushSubscribeView(generics.GenericAPIView):
    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, **kwargs):
        error, response = svc_notification_subscribe(request.data, kwargs["profile"])
        return get_standard_response(error, response)


class NotificationListView(generics.GenericAPIView):
    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def get(self, request, **kwargs):
        error, notifications = svc_notification_get_notifications(kwargs["profile"])
        return get_paginated_response(self, error, notifications, NotificationSerializer)


class NotificationReadView(generics.GenericAPIView):
    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, notification_id: uuid.UUID, **kwargs):
        error, response = svc_notification_mark_notification_read(notification_id)
        return get_standard_response(error, response)
