import logging
import uuid

from fact.services.helper import (
    svc_fact_helper_create_fact,
    svc_fact_helper_get_facts,
    svc_fact_helper_get_serialized_facts,
    svc_fact_helper_run_validations_to_create_fact,
    svc_fact_helper_run_validations_to_get_facts,
    svc_fact_helper_validate_and_get_fact_type,
    svc_fact_helper_validate_and_get_game,
    svc_fact_helper_validate_and_get_team,
)

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


def svc_fact_create_fact(request_data: dict, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_fact_helper_run_validations_to_create_fact(request_data)
    if error:
        return error, None

    error, fact_type = svc_fact_helper_validate_and_get_fact_type(request_data)
    if error:
        return error, None

    error, game = svc_fact_helper_validate_and_get_game(request_data["game_id"])
    if error:
        return error, None

    error, team = svc_fact_helper_validate_and_get_team(request_data["team_id"])
    if error:
        return error, None

    fact = svc_fact_helper_create_fact(fact_type, game, team, request_data["fact_info"])

    if serialized:
        fact = svc_fact_helper_get_serialized_facts(fact, many=False)

    return ErrorCode(ErrorCode.CREATED), fact


def svc_fact_get_facts(request_data: dict, serialized: bool = False):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_fact_helper_run_validations_to_get_facts(request_data)
    if error:
        return error, None

    error, game = svc_fact_helper_validate_and_get_game(request_data["game_id"])
    if error:
        return error, None

    error, team = svc_fact_helper_validate_and_get_team(request_data["team_id"])
    if error:
        return error, None

    facts = svc_fact_helper_get_facts(game, team, request_data)

    if serialized:
        facts = svc_fact_helper_get_serialized_facts(facts, many=True)

    return ErrorCode(ErrorCode.SUCCESS), facts
