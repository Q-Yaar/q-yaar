import logging
import uuid

from django.db.models import QuerySet
from game.models import Game, Team
from game.services.helper import (
    svc_game_helper_get_game_by_id,
    svc_game_helper_get_player_ids_for_game,
    svc_game_helper_get_player_ids_for_team,
    svc_game_helper_get_player_ids_for_teams,
    svc_game_helper_get_team_by_id,
    svc_game_helper_get_teams_for_game,
    svc_game_helper_verify_game_master_belongs_to_game,
    svc_game_helper_verify_player_belongs_to_game,
    svc_game_helper_verify_player_is_in_team,
)
from profile_game_master.models import GameMasterProfile
from profile_player.models import PlayerProfile

logger = logging.getLogger(__name__)


def svc_game_get_team_by_id(team_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_get_team_by_id(team_id=team_id)


def svc_game_verify_player_belongs_to_team(player: PlayerProfile, team: Team):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_verify_player_is_in_team(player=player, team=team)


def svc_game_verify_player_belongs_to_game(player: PlayerProfile, game: Game):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_verify_player_belongs_to_game(player=player, game=game)


def svc_game_verify_game_master_belongs_to_game(game_master: GameMasterProfile, game: Game):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_verify_game_master_belongs_to_game(game_master=game_master, game=game)


def svc_game_get_game_by_id(game_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_get_game_by_id(game_id=game_id)


def svc_game_get_team_by_id(team_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_get_team_by_id(team_id=team_id)


def svc_game_get_player_teams_for_game(game: Game):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_get_teams_for_game(game=game, request_data={"team_type": "PLAYER"})


def svc_game_get_player_ids_for_game(game: Game):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_get_player_ids_for_game(game=game)


def svc_game_get_player_ids_for_team(team: Team):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_get_player_ids_for_team(team=team)


def svc_game_get_player_ids_for_teams(teams: QuerySet[Team]):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_get_player_ids_for_teams(teams=teams)
