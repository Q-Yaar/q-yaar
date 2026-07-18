import logging
import uuid

from common.constants import UserRolesType
from game.api.serializers import GameDetailSerializer, GameSerializer, TeamSerializer
from game.services.error_codes import ErrorCode
from game.services.helper import (
    svc_game_helper_create_game,
    svc_game_helper_create_team,
    svc_game_helper_end_game,
    svc_game_helper_explore_games,
    svc_game_helper_get_game_by_id,
    svc_game_helper_get_game_for_player,
    svc_game_helper_get_game_type_from_request_data,
    svc_game_helper_get_game_visibility_mode_from_request_data,
    svc_game_helper_get_games_for_game_master,
    svc_game_helper_get_players_from_request_data,
    svc_game_helper_get_spectator_team,
    svc_game_helper_get_team_by_id,
    svc_game_helper_get_teams_for_game,
    svc_game_helper_get_teams_for_player,
    svc_game_helper_join_team,
    svc_game_helper_run_validations_for_game_creation,
    svc_game_helper_run_validations_for_game_update,
    svc_game_helper_run_validations_for_team_creation,
    svc_game_helper_run_validations_for_team_update,
    svc_game_helper_start_game,
    svc_game_helper_update_game,
    svc_game_helper_update_team,
)
from profile_game_master.models import GameMasterProfile
from profile_player.models import PlayerProfile

logger = logging.getLogger(__name__)


def svc_game_create_game(request_data: dict, profile: GameMasterProfile, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_game_helper_run_validations_for_game_creation(request_data=request_data)
    if error:
        return error, None

    game_type = svc_game_helper_get_game_type_from_request_data(request_data=request_data)
    game_visibility_mode = svc_game_helper_get_game_visibility_mode_from_request_data(request_data=request_data)

    game = svc_game_helper_create_game(
        game_type=game_type,
        game_visibility_mode=game_visibility_mode,
        name=request_data["name"],
        description=request_data["description"],
        created_by=profile,
    )

    if serialized:
        game = GameDetailSerializer(game, many=False).data

    return ErrorCode(ErrorCode.CREATED), game


def svc_game_get_games(request_data: dict, role: UserRolesType, profile: GameMasterProfile | PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    if role == UserRolesType.GAME_MASTER:
        games = svc_game_helper_get_games_for_game_master(request_data=request_data, game_master=profile)
    elif role == UserRolesType.PLAYER:
        games = svc_game_helper_get_game_for_player(player=profile)

    return ErrorCode(ErrorCode.SUCCESS), games


def svc_game_explore_games(profile: PlayerProfile, request_data: dict, serialized: bool = False):
    logger.debug(f">> ARGS: {locals()}")

    games = svc_game_helper_explore_games(player=profile, request_data=request_data)

    if serialized:
        games = GameSerializer(games, many=True).data

    return ErrorCode(ErrorCode.SUCCESS), games


def svc_game_get_game_by_id(game_id: uuid.UUID, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, game = svc_game_helper_get_game_by_id(game_id=game_id)
    if error:
        return error, None

    if serialized:
        game = GameDetailSerializer(game, many=False).data

    return ErrorCode(ErrorCode.SUCCESS), game


def svc_game_start_game(game_id: uuid.UUID, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, game = svc_game_helper_get_game_by_id(game_id=game_id)
    if error:
        return error, None

    error, game = svc_game_helper_start_game(game=game)
    if error:
        return error, None

    if serialized:
        game = GameDetailSerializer(game, many=False).data

    return ErrorCode(ErrorCode.SUCCESS), game


def svc_game_end_game(game_id: uuid.UUID, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, game = svc_game_helper_get_game_by_id(game_id=game_id)
    if error:
        return error, None

    error, game = svc_game_helper_end_game(game=game)
    if error:
        return error, None

    if serialized:
        game = GameDetailSerializer(game, many=False).data

    return ErrorCode(ErrorCode.SUCCESS), game


def svc_game_create_team(game_id: str, request_data: dict, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_game_helper_run_validations_for_team_creation(request_data=request_data)
    if error:
        return error, None

    error, game = svc_game_helper_get_game_by_id(game_id=game_id)
    if error:
        return error, None

    error, players = svc_game_helper_get_players_from_request_data(request_data)
    if error:
        return error, None

    error, team = svc_game_helper_create_team(game, request_data["team_name"], request_data["team_colour"], players)
    if error:
        return error, None

    if serialized:
        team = TeamSerializer(team, many=False).data

    return ErrorCode(ErrorCode.CREATED), team


def svc_game_get_teams_for_game(game_id: str, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, game = svc_game_helper_get_game_by_id(game_id=game_id)
    if error:
        return error, None

    teams = svc_game_helper_get_teams_for_game(game)

    if serialized:
        teams = TeamSerializer(teams, many=True).data

    return ErrorCode(ErrorCode.SUCCESS), teams


def svc_game_get_team_for_player(game_id: str, player: PlayerProfile, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, game = svc_game_helper_get_game_by_id(game_id=game_id)
    if error:
        return error, None

    error, team = svc_game_helper_get_teams_for_player(game=game, player=player)
    if error:
        return error, None

    if serialized:
        team = TeamSerializer(team, many=False).data

    return ErrorCode(ErrorCode.SUCCESS), team


def svc_game_update_team(game_id: str, team_id: str, request_data: dict, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, game = svc_game_helper_get_game_by_id(game_id=game_id)
    if error:
        return error, None

    error = svc_game_helper_run_validations_for_team_update(game=game)
    if error:
        return error, None

    error, team = svc_game_helper_get_team_by_id(team_id=team_id)
    if error:
        return error, None

    team = svc_game_helper_update_team(team=team, request_data=request_data)

    if serialized:
        team = TeamSerializer(team, many=False).data

    return ErrorCode(ErrorCode.SUCCESS), team


def svc_game_update_game(game_id: str, request_data: dict, profile: GameMasterProfile, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, game = svc_game_helper_get_game_by_id(game_id=game_id)
    if error:
        return error, None

    error = svc_game_helper_run_validations_for_game_update(game=game, profile=profile, request_data=request_data)
    if error:
        return error, None

    game = svc_game_helper_update_game(game=game, request_data=request_data)

    if serialized:
        game = GameDetailSerializer(game, many=False).data

    return ErrorCode(ErrorCode.SUCCESS), game


def svc_game_join_team(game_id: str, team_id: str, player: PlayerProfile, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, game = svc_game_helper_get_game_by_id(game_id=game_id)
    if error:
        return error, None

    error, team = svc_game_helper_get_team_by_id(team_id=team_id)
    if error:
        return error, None

    if team.game != game:
        return ErrorCode(ErrorCode.INVALID_TEAM_ID, team_id=team_id), None

    svc_game_helper_join_team(game=game, team=team, player=player)

    if serialized:
        game = GameDetailSerializer(game, many=False).data

    return ErrorCode(ErrorCode.SUCCESS), game


def svc_game_join_game(game_id: str, player: PlayerProfile, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, game = svc_game_helper_get_game_by_id(game_id=game_id)
    if error:
        return error, None

    error, spectator_team = svc_game_helper_get_spectator_team(game=game)
    if error:
        return error, None

    svc_game_helper_join_team(game=game, team=spectator_team, player=player)

    if serialized:
        game = GameDetailSerializer(game, many=False).data

    return ErrorCode(ErrorCode.SUCCESS), game
