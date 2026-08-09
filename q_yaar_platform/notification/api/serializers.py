from notification.models import PushNotificationHistory
from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer):
    notification_id = serializers.SerializerMethodField()

    class Meta:
        model = PushNotificationHistory
        fields = ["notification_id", "title", "message", "payload", "is_read", "created", "modified"]

    def get_notification_id(self, obj: PushNotificationHistory):
        return str(obj.get_external_id())
