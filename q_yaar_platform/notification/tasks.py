from account.services.interfacer import svc_account_get_platform_user_by_id
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from notification.services.push_service import send_push_notification

logger = get_task_logger(__name__)


@shared_task(name="send_notification", queue="notification", bind=True, max_retries=3, soft_time_limit=300)
def send_notification(self, user_id: str, title: str, message: str, payload: dict):
    logger.debug(f">> ARGS: {locals()}")

    if settings.SKIP_NOTIFICATIONS:
        logger.debug("Notifications are disabled")
        return

    error, platform_user = svc_account_get_platform_user_by_id(user_id)

    if error:
        logger.error(f"Error getting platform user: {error.code} - {error._message}")
        return

    send_push_notification(platform_user, title, message, payload)

    logger.debug(f"Notification sent to user {platform_user.email}")
