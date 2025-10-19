from django.urls import path

from . import views

app_name = "game"

urlpatterns = [
    path(r"", views.GameListView.as_view(), name="handler-game-list"),
    path(r"<uuid:game_id>/start", views.GameStartView.as_view(), name="handler-game-start"),
    path(r"<uuid:game_id>/end", views.GameEndView.as_view(), name="handler-game-end"),

    path(r"<uuid:game_id>/team/", views.TeamListView.as_view(), name="handler-team-list"),
]
