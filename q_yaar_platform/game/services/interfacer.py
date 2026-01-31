import logging
import uuid

from game.models import Team
from game.services.helper import (
    svc_game_helper_get_game_by_id,
    svc_game_helper_get_team_by_id,
    svc_game_helper_verify_player_is_in_team,
)
from profile_player.models import PlayerProfile

logger = logging.getLogger(__name__)


def svc_game_get_team_by_id(team_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_get_team_by_id(team_id=team_id)


def svc_game_verify_player_belongs_to_team(player: PlayerProfile, team: Team):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_verify_player_is_in_team(player=player, team=team)


def svc_game_get_game_by_id(game_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_get_game_by_id(game_id=game_id)


def svc_game_get_team_by_id(team_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_get_team_by_id(team_id=team_id)
