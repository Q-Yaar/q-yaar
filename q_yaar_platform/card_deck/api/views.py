import logging

from card_deck.api.serializers import CardSerializer
from card_deck.services.core import (
    svc_card_deck_bulk_create_cards,
    svc_card_deck_get_cards_by_tag,
    svc_card_deck_get_list_of_tags,
)
from common.response import get_paginated_response, get_standard_response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class CardsListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardsListView")
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        error, cards = svc_card_deck_get_cards_by_tag(request.query_params)
        return get_paginated_response(self, error, cards, CardSerializer)

    def post(self, request):
        error, cards = svc_card_deck_bulk_create_cards(request.data)
        return get_paginated_response(self, error, cards, CardSerializer)


class CardsTagsListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardsTagsListView")
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        error, tags = svc_card_deck_get_list_of_tags()
        return get_standard_response(error, tags)
