import logging

from notification.services.helper import (
    svc_notification_helper_get_notification_by_id,
    svc_notification_helper_get_notification_list,
    svc_notification_helper_get_serialized_notifications,
    svc_notification_helper_get_vapid_public_key,
    svc_notification_helper_mark_all_notifications_read,
    svc_notification_helper_mark_notification_read,
    svc_notification_helper_save_subscription_info,
    svc_notification_helper_validate_subscription_request_data,
)
from profile_player.models import PlayerProfile

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


def svc_notification_get_webpush_keys():
    logger.debug(f">> ARGS: {locals()}")

    vapid_public_key = svc_notification_helper_get_vapid_public_key()

    return ErrorCode(ErrorCode.SUCCESS), {"vapid_public_key": vapid_public_key}


def svc_notification_subscribe(request_data: dict, profile: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_notification_helper_validate_subscription_request_data(request_data)
    if error:
        return error, None

    svc_notification_helper_save_subscription_info(request_data, profile.platform_user)

    return ErrorCode(ErrorCode.SUCCESS), {"status": "subscribed"}


def svc_notification_get_notifications(profile: PlayerProfile, request_data: dict, serialized: bool = False):
    logger.debug(f">> ARGS: {locals()}")

    notifications = svc_notification_helper_get_notification_list(profile.platform_user, request_data)

    if serialized:
        notifications = svc_notification_helper_get_serialized_notifications(notifications, many=True)

    return ErrorCode(ErrorCode.SUCCESS), notifications


def svc_notification_mark_notification_read(notification_id: str):
    logger.debug(f">> ARGS: {locals()}")

    error, notification = svc_notification_helper_get_notification_by_id(notification_id)
    if error:
        return error, None

    svc_notification_helper_mark_notification_read(notification)

    return ErrorCode(ErrorCode.NO_CONTENT), None


def svc_notification_mark_all_notifications_read(profile: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    svc_notification_helper_mark_all_notifications_read(profile.platform_user)

    return ErrorCode(ErrorCode.NO_CONTENT), None
