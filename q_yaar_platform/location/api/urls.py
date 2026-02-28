from django.urls import path

from .views import (
    LocationPingsView,
    PlayerLastLocationView,
    LocationSharingSettingView,
    LocationTrackingCodeUpdateView,
)

app_name = "location"

urlpatterns = [
    path("pings/", LocationPingsView.as_view(), name="location-pings"),
    path("players/<uuid:player_id>/last/", PlayerLastLocationView.as_view(), name="player-last-location"),
    path("settings/share/", LocationSharingSettingView.as_view(), name="location-sharing-settings"),
    path("settings/tracking-code/", LocationTrackingCodeUpdateView.as_view(), name="location-tracking-code-update"),
]
