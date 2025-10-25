from django.urls import path

from . import views

app_name = "card_deck"

urlpatterns = [
    # POST - Login
    path(r"", views.CardsListView.as_view(), name="handler-cards-list"),
    path(r"tags/", views.CardsTagsListView.as_view(), name="handler-cards-tags-list"),
    path(r"deck/<uuid:team_id>/", views.CardDeckView.as_view(), name="handler-card-deck"),
    path(r"deck/<uuid:team_id>/stats", views.CardStatsView.as_view(), name="handler-card-stats"),
    path(r"deck/<uuid:team_id>/pile/hand", views.CardHandListView.as_view(), name="handler-card-hand-list"),
    path(r"deck/<uuid:team_id>/pile/discard", views.CardDiscardListView.as_view(), name="handler-card-discard-list"),
    path(r"deck/<uuid:team_id>/peek", views.CardPeekView.as_view(), name="handler-card-peek"),
    path(r"deck/<uuid:team_id>/cards/<uuid:card_id>/draw", views.CardDrawView.as_view(), name="handler-card-draw"),
    path(
        r"deck/<uuid:team_id>/cards/<uuid:card_id>/discard",
        views.CardDiscardView.as_view(),
        name="handler-card-discard",
    ),
    path(
        r"deck/<uuid:team_id>/cards/<uuid:card_id>/return", views.CardReturnView.as_view(), name="handler-card-return"
    ),
]
