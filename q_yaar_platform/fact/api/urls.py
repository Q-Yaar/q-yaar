from django.urls import path

from . import views

app_name = "fact"

urlpatterns = [
    path(r"", views.FactsListView.as_view(), name="handler-facts-list"),
    path(r"<uuid:fact_id>", views.FactDetailView.as_view(), name="handler-fact-detail"),
]
