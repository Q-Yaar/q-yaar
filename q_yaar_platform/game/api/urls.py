from django.urls import path

from . import views

app_name = "game"

urlpatterns = [
    path(r"", views.GameListView.as_view(), name="handler-game-list"),
]
