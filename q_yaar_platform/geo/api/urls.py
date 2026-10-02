from django.urls import path

from . import views

app_name = "geo"

urlpatterns = [
    path(r"", views.GeoFeaturesListView.as_view(), name="handler-geo-features-list"),
    path(r"within", views.GeoFeaturesWithinView.as_view(), name="handler-geo-features-within"),
    path(r"<int:feature_id>", views.GeoFeatureDetailView.as_view(), name="handler-geo-feature-detail"),
]
