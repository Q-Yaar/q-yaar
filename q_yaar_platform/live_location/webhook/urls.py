from django.urls import path

from . import views

app_name = "live_location_webhook"

urlpatterns = [
    path(
        r"<str:tracker_client>/track/<uuid:tracking_id>",
        views.LocationTrackingView.as_view(),
        name="handler-location-tracking",
    ),
]
