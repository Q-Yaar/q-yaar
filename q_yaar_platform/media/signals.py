"""Delete the backing S3 object when an Asset row is removed.

Catches all deletion paths (user CASCADE, game CASCADE, explicit delete) in
one place. The DB row is gone by post_delete time, so the object_key is read
from the instance before it's discarded. Deletion is offloaded to a celery
task so a slow or failing S3 call can't block or break the delete path.
"""

import logging

from django.db.models.signals import post_delete
from django.dispatch import receiver

from media.models import Asset
from media.tasks import delete_asset_object

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Asset)
def delete_asset_object_signal(sender, instance: Asset, **kwargs):
    logger.debug(f">> ARGS: {locals()}")

    delete_asset_object.delay(instance.object_key)
