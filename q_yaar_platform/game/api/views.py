import logging
import uuid

from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_paginated_response, get_standard_response
from game.api.serializers import GameSerializer
from game.services.core import (
    svc_game_create_game,
    svc_game_create_team,
    svc_game_end_game,
    svc_game_get_games,
    svc_game_get_team_for_player,
    svc_game_get_teams_for_game,
    svc_game_start_game,
)
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


class GameStartView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".GameStartView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def post(self, request, game_id: uuid.UUID, **kwargs):
        error, response = svc_game_start_game(game_id=game_id)
        return get_standard_response(error, response)


class GameEndView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".GameEndView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def post(self, request, game_id: uuid.UUID, **kwargs):
        error, response = svc_game_end_game(game_id=game_id)
        return get_standard_response(error, response)


class TeamListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".TeamListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER, UserRolesType.PLAYER])
    def get(self, request, game_id: uuid.UUID, **kwargs):
        error, response = svc_game_get_teams_for_game(game_id=game_id)
        return get_standard_response(error, response)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def post(self, request, game_id: uuid.UUID, **kwargs):
        error, response = svc_game_create_team(game_id, request.data)
        return get_standard_response(error, response)


class PlayerTeamView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".PlayerTeamView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def get(self, request, game_id: uuid.UUID, **kwargs):
        error, response = svc_game_get_team_for_player(game_id, kwargs["profile"])
        return get_standard_response(error, response)
