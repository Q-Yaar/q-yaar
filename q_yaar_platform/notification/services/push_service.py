import logging

from account.models import PlatformUser
from django.contrib.auth import get_user_model
from notification.models import PushNotificationHistory
from webpush import send_user_notification

logger = logging.getLogger(__name__)
User = get_user_model()


def send_push_notification(user: PlatformUser, title: str, message: str, payload: dict) -> PushNotificationHistory:
    logger.debug(f">> ARGS: {locals()}")

    notification = PushNotificationHistory.create(user=user, title=title, message=message, payload=payload)

    push_payload = {"head": title, "body": message, **payload}

    try:
        send_user_notification(user=user, payload=push_payload, ttl=1000)
    except Exception as e:
        logger.error(f"Failed to send webpush notification to user {user.email}: {e}")

    return notification


# TODO: Not scalable currently, need to design group notifications properly later.
# def send_group_push_notification(group_name: str, title: str, message: str, payload: dict):
#     logger.debug(f">> ARGS: {locals()}")

#     # Get all users in the group
#     users_in_group = User.objects.filter(webpush_info__group__name=group_name).distinct()

#     notifications = [
#         PushNotificationHistory.create(user=user, title=title, message=message, payload=payload)
#         for user in users_in_group
#     ]

#     push_payload = {"head": title, "body": message, **payload}

#     try:
#         send_group_notification(group_name=group_name, payload=push_payload, ttl=1000)
#     except Exception as e:
#         logger.error(f"Failed to send group webpush notification to group {group_name}: {e}")
