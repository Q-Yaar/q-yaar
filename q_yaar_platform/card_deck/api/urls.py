from django.urls import path

from . import views

app_name = "card_deck"

urlpatterns = [
    # POST - Login
    path(r"", views.CardsListView.as_view(), name="handler-cards-list"),
    path(r"tags/", views.CardsTagsListView.as_view(), name="handler-cards-tags-list"),
    path(r"deck/<uuid:team_id>/", views.CardDeckView.as_view(), name="handler-card-deck"),
    path(r"deck/<uuid:team_id>/stats", views.CardStatsView.as_view(), name="handler-card-stats"),
    path(r"deck/<uuid:team_id>/peek", views.CardPeekView.as_view(), name="handler-card-peek"),
]
