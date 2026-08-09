import logging
import uuid

from account.models import PlatformUser
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from notification.api.serializers import NotificationSerializer
from notification.models import PushNotificationHistory
from webpush.models import Group, PushInformation, SubscriptionInfo

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


def svc_notification_helper_get_vapid_public_key():
    return settings.VAPID_PUBLIC_KEY


def svc_notification_helper_validate_subscription_request_data(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("endpoint"):
        return ErrorCode(ErrorCode.MISSING_ENDPOINT)

    if not request_data.get("keys"):
        return ErrorCode(ErrorCode.MISSING_KEYS)

    if not request_data.get("keys").get("p256dh"):
        return ErrorCode(ErrorCode.MISSING_P256DH)

    if not request_data.get("keys").get("auth"):
        return ErrorCode(ErrorCode.MISSING_AUTH)

    return None


def svc_notification_helper_save_subscription_info(request_data: dict, user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    endpoint = request_data["endpoint"]
    p256dh = request_data["keys"]["p256dh"]
    auth = request_data["keys"]["auth"]
    browser = request_data.get("browser", "")
    group_name = request_data.get("group", "")

    sub, created = SubscriptionInfo.objects.get_or_create(
        endpoint=endpoint, defaults={"p256dh": p256dh, "auth": auth, "browser": browser}
    )
    if not created:
        sub.p256dh = p256dh
        sub.auth = auth
        sub.browser = browser
        sub.save()

    group_obj = None
    if group_name:
        group_obj, _ = Group.objects.get_or_create(name=group_name)

    # Link to User and Group
    # Django-webpush PushInformation can only link user or group or both.
    # But if we change the group of an existing subscription, we should update it.
    push_info, pi_created = PushInformation.objects.get_or_create(user=user, subscription=sub)

    if push_info.group != group_obj:
        push_info.group = group_obj
        push_info.save()


def svc_notification_helper_get_notification_list(user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    notifications = PushNotificationHistory.objects.filter(user=user).order_by("-created")
    return notifications


def svc_notification_helper_get_serialized_notifications(
    notifications: PushNotificationHistory | list[PushNotificationHistory], many: bool
):
    logger.debug(f">> ARGS: {locals()}")

    return NotificationSerializer(notifications, many=many).data


def svc_notification_helper_get_notification_by_id(notification_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    try:
        return None, PushNotificationHistory.objects.get(external_id=notification_id)
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.INVALID_NOTIFICATION_ID, notification_id=notification_id), None


def svc_notification_helper_mark_notification_read(notification: PushNotificationHistory):
    logger.debug(f">> ARGS: {locals()}")

    notification.is_read = True
    notification.save()
    return None
