from django.urls import path

from . import views

app_name = "media"

urlpatterns = [
    path(r"", views.AssetListView.as_view(), name="handler-asset-list"),
    path(r"<uuid:asset_id>", views.AssetDetailView.as_view(), name="handler-asset-detail"),
    path(r"<uuid:asset_id>/confirm", views.AssetConfirmView.as_view(), name="handler-asset-confirm"),
]
