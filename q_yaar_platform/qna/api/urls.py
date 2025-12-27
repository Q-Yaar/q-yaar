from django.urls import path

from . import views

app_name = "qna"

urlpatterns = [
    # POST - Login
    path(r"rewards/", views.RewardsListView.as_view(), name="handler-rewards-list"),
    path(r"categories/", views.CategoriesListView.as_view(), name="handler-categories-list"),
]
