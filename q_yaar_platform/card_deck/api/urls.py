from django.urls import path

from . import views

app_name = "card_deck"

urlpatterns = [
    # POST - Login
    path(r"", views.CardsListView.as_view(), name="handler-cards-list"),
]
