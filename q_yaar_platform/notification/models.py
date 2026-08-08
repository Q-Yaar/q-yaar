from account.models import PlatformUser
from common.abstract_models import AbstractExternalFacing, AbstractTimeStamped
from django.db import models


class PushNotificationHistory(AbstractExternalFacing, AbstractTimeStamped):
    user = models.ForeignKey(PlatformUser, related_name="push_notifications", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    payload = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.title}"

    @classmethod
    def create(cls, user: PlatformUser, title: str, message: str, payload: dict) -> "PushNotificationHistory":
        notification = cls(user=user, title=title, message=message, payload=payload)
        notification.save()
        return notification
