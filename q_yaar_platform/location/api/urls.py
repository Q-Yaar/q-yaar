from django.urls import path

from .views import (
    LocationPingsView,
    PlayerLastLocationView,
    LocationSharingSettingView,
)

app_name = "location"

urlpatterns = [
    path("pings/", LocationPingsView.as_view(), name="location-pings"),
    path("players/<uuid:player_id>/last/", PlayerLastLocationView.as_view(), name="player-last-location"),
    path("settings/", LocationSharingSettingView.as_view(), name="location-sharing-settings"),
]
