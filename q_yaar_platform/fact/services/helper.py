import logging
import uuid

from common.constants import FactType
from fact.api.serializers import FactSerializer
from fact.models import Fact
from game.models import Game, Team
from game.services.interfacer import svc_game_get_game_by_id, svc_game_get_team_by_id

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


def svc_fact_helper_run_validations_to_create_fact(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("fact_type"):
        return ErrorCode(ErrorCode.MISSING_FACT_TYPE)

    if not request_data.get("fact_info"):
        return ErrorCode(ErrorCode.MISSING_FACT_INFO)

    if not request_data.get("game_id"):
        return ErrorCode(ErrorCode.MISSING_GAME_ID)

    if not request_data.get("team_id"):
        return ErrorCode(ErrorCode.MISSING_TEAM_ID)

    return None


def svc_fact_helper_validate_and_get_fact_type(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    try:
        return None, FactType.tokentype_from_string(request_data["fact_type"])
    except KeyError:
        return ErrorCode(ErrorCode.INVALID_FACT_TYPE, fact_type=request_data["fact_type"]), None


def svc_fact_helper_run_validations_to_get_facts(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("game_id"):
        return ErrorCode(ErrorCode.MISSING_GAME_ID)

    if not request_data.get("team_id"):
        return ErrorCode(ErrorCode.MISSING_TEAM_ID)

    if request_data.get("fact_type"):
        error, fact_type = svc_fact_helper_validate_and_get_fact_type(request_data)
        if error:
            return error

    return None


def svc_fact_helper_apply_filters_for_fact(request_data: dict, facts: list[Fact]):
    logger.debug(f">> ARGS: {locals()}")

    if request_data.get("fact_type"):
        facts = facts.filter(fact_type=FactType.tokentype_from_string(request_data["fact_type"]))

    return facts


def svc_fact_helper_validate_and_get_game(game_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_get_game_by_id(game_id)


def svc_fact_helper_validate_and_get_team(team_id: uuid.UUID):
    return svc_game_get_team_by_id(team_id)


def svc_fact_helper_create_fact(fact_type: FactType, game: Game, target_team: Team, fact_info: dict) -> Fact:
    logger.debug(f">> ARGS: {locals()}")

    fact = Fact.create(fact_type=fact_type, game=game, target_team=target_team, fact_info=fact_info)

    return fact


def svc_fact_helper_get_serialized_facts(facts: Fact | list[Fact], many: bool):
    logger.debug(f">> ARGS: {locals()}")

    return FactSerializer(facts, many=many).data


def svc_fact_helper_get_facts(game: Game, team: Team, request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    facts = Fact.objects.filter(game=game, target_team=team).order_by("created")

    facts = svc_fact_helper_apply_filters_for_fact(request_data, facts)

    return facts


if __name__ == "__main__":
    svc_fact_helper_validate_and_get_fact_type({"fact_type": "TEXT"})
