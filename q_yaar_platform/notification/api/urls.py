from django.urls import path

from . import views

urlpatterns = [
    path(r"webpush/keys", views.WebPushKeysView.as_view(), name="webpush-keys"),
    path(r"webpush/subscribe", views.WebPushSubscribeView.as_view(), name="webpush-subscribe"),
    path(r"<uuid:notification_id>", views.NotificationReadView.as_view(), name="notification-read"),
    path(r"", views.NotificationListView.as_view(), name="notification-history"),
]
