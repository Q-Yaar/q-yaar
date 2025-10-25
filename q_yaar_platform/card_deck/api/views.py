import logging
import uuid

from card_deck.api.serializers import CardSerializer
from card_deck.services.core import (
    svc_card_deck_bulk_create_cards,
    svc_card_deck_create_deck_for_team,
    svc_card_deck_create_tag,
    svc_card_deck_discard_card,
    svc_card_deck_draw_card,
    svc_card_deck_get_card_stats,
    svc_card_deck_get_cards_by_tag,
    svc_card_deck_get_deck_for_team,
    svc_card_deck_get_list_of_tags,
    svc_card_deck_peek_cards,
    svc_card_deck_return_card,
    svc_card_deck_view_discard_pile,
    svc_card_deck_view_hand_pile,
)
from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_paginated_response, get_standard_response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class CardsListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardsListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER, UserRolesType.GAME_MASTER])
    def get(self, request, **kwargs):
        error, cards = svc_card_deck_get_cards_by_tag(request.query_params)
        return get_paginated_response(self, error, cards, CardSerializer)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def post(self, request, **kwargs):
        error, cards = svc_card_deck_bulk_create_cards(request.data)
        return get_paginated_response(self, error, cards, CardSerializer)


class CardsTagsListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardsTagsListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def get(self, request, **kwargs):
        error, tags = svc_card_deck_get_list_of_tags()
        return get_standard_response(error, tags)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def post(self, request, **kwargs):
        error, tag = svc_card_deck_create_tag(request.data)
        return get_standard_response(error, tag)


class CardDeckView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardDeckView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def get(self, request, team_id: uuid.UUID, **kwargs):
        error, cards = svc_card_deck_get_deck_for_team(team_id)
        return get_paginated_response(self, error, cards, CardSerializer)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def post(self, request, team_id: uuid.UUID, **kwargs):
        error, response = svc_card_deck_create_deck_for_team(request.data, team_id)
        return get_standard_response(error, response)


class CardStatsView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardStatsView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def get(self, request, team_id: uuid.UUID, **kwargs):
        error, response = svc_card_deck_get_card_stats(team_id, kwargs["profile"])
        return get_standard_response(error, response)


class CardHandListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardHandListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def get(self, request, team_id: uuid.UUID, **kwargs):
        error, response = svc_card_deck_view_hand_pile(team_id, kwargs["profile"])
        return get_standard_response(error, response)


class CardDiscardListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardDiscardListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def get(self, request, team_id: uuid.UUID, **kwargs):
        error, response = svc_card_deck_view_discard_pile(team_id, kwargs["profile"])
        return get_standard_response(error, response)


class CardPeekView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardPeekView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, team_id: uuid.UUID, **kwargs):
        error, response = svc_card_deck_peek_cards(team_id, kwargs["profile"], request.data)
        return get_standard_response(error, response)


class CardDrawView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardDrawView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, team_id: uuid.UUID, card_id: uuid.UUID, **kwargs):
        error, response = svc_card_deck_draw_card(team_id, kwargs["profile"], card_id)
        return get_standard_response(error, response)


class CardDiscardView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardDiscardView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, team_id: uuid.UUID, card_id: uuid.UUID, **kwargs):
        error, response = svc_card_deck_discard_card(team_id, kwargs["profile"], card_id)
        return get_standard_response(error, response)


class CardReturnView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CardReturnView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, team_id: uuid.UUID, card_id: uuid.UUID, **kwargs):
        error, response = svc_card_deck_return_card(team_id, kwargs["profile"], card_id)
        return get_standard_response(error, response)
