import logging
import uuid

from game.services.helper import svc_game_helper_get_team_by_id

logger = logging.getLogger(__name__)


def svc_game_get_team_by_id(team_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_helper_get_team_by_id(team_id=team_id)
