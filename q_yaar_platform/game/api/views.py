import logging

from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_paginated_response, get_standard_response
from game.api.serializers import GameSerializer
from game.services.core import svc_game_create_game, svc_game_get_games
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class GameListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".GameListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER, UserRolesType.PLAYER])
    def get(self, request, **kwargs):
        error, games = svc_game_get_games(request.query_params, kwargs["role"], kwargs["profile"])
        return get_paginated_response(self, error, games, GameSerializer)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def post(self, request, **kwargs):
        error, response = svc_game_create_game(request.data, kwargs["profile"])
        return get_standard_response(error, response)
