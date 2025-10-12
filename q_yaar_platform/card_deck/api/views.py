import logging

from card_deck.api.serializers import CardSerializer
from card_deck.services.core import svc_card_deck_get_cards_by_tag
from common.response import get_paginated_response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class CardsListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardsListView")
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        error, cards = svc_card_deck_get_cards_by_tag(request.query_params)
        return get_paginated_response(self, error, cards, CardSerializer)
