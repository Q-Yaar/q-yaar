import logging

from common.constants import UserRolesType
from game.api.serializers import GameSerializer
from game.services.error_codes import ErrorCode
from game.services.helper import (
    svc_game_helper_create_game,
    svc_game_helper_get_game_for_player,
    svc_game_helper_get_game_type_from_request_data,
    svc_game_helper_get_games_for_game_master,
    svc_game_helper_get_players_from_request_data,
    svc_game_helper_get_teams_info_from_request_data,
    svc_game_helper_run_validations_for_game_creation,
)
from profile_game_master.models import GameMasterProfile

logger = logging.getLogger(__name__)


def svc_game_create_game(request_data: dict, profile: GameMasterProfile, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_game_helper_run_validations_for_game_creation(request_data=request_data)
    if error:
        return error, None

    game_type = svc_game_helper_get_game_type_from_request_data(request_data=request_data)
    players_list = svc_game_helper_get_players_from_request_data(request_data=request_data)
    teams_info = svc_game_helper_get_teams_info_from_request_data(request_data=request_data)

    game = svc_game_helper_create_game(
        game_type=game_type,
        name=request_data["name"],
        description=request_data["description"],
        created_by=profile,
        players=players_list,
        teams_info=teams_info,
    )

    if serialized:
        game = GameSerializer(game, many=False).data

    return ErrorCode(ErrorCode.CREATED), game


def svc_game_get_games(request_data: dict, role: UserRolesType, profile: GameMasterProfile):
    logger.debug(f">> ARGS: {locals()}")

    if role == UserRolesType.GAME_MASTER:
        games = svc_game_helper_get_games_for_game_master(request_data=request_data, game_master=profile)
    elif role == UserRolesType.PLAYER:
        games = svc_game_helper_get_game_for_player(player=profile)

    return ErrorCode(ErrorCode.SUCCESS), games
