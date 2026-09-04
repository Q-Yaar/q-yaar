from celery import shared_task
from celery.utils.log import get_task_logger

from media.services.helper import svc_media_helper_delete_object

logger = get_task_logger(__name__)


@shared_task(name="delete_asset_object", queue="default", bind=True, max_retries=3, soft_time_limit=60)
def delete_asset_object(self, object_key: str):
    logger.debug(f">> ARGS: {locals()}")

    svc_media_helper_delete_object(object_key)
