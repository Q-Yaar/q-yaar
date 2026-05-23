from django.urls import path

from . import views

app_name = "live_location"

urlpatterns = [
    path(r"games/<uuid:game_id>/", views.LastLocationListView.as_view(), name="handler-last-location-list"),
    path(r"settings", views.LocationSettingsView.as_view(), name="handler-location-settings"),
    path(r"enable", views.LocationSharingEnableView.as_view(), name="handler-location-sharing-enable"),
]
