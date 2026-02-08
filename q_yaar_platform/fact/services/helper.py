import logging
import uuid

from common.constants import FactType
from django.db.models import ObjectDoesNotExist
from fact.api.serializers import FactSerializer
from fact.models import Fact
from fact.popo.fact_meta import FactMetaConfig
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

    if request_data.get("fact_type"):
        error, fact_type = svc_fact_helper_validate_and_get_fact_type(request_data)
        if error:
            return error

    return None


def svc_fact_helper_run_validations_to_update_fact(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not "fact_info" in request_data:
        return ErrorCode(ErrorCode.MISSING_FACT_INFO)

    return None


def svc_fact_helper_apply_filters_for_fact(request_data: dict, facts: list[Fact]):
    logger.debug(f">> ARGS: {locals()}")

    if request_data.get("fact_type"):
        facts = facts.filter(fact_type=FactType.tokentype_from_string(request_data["fact_type"]))

    if request_data.get("team_id"):
        error, team = svc_fact_helper_validate_and_get_team(request_data["team_id"])
        if error:
            return error, None
        facts = facts.filter(target_team=team)

    return None, facts


def svc_fact_helper_validate_and_get_game(game_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_get_game_by_id(game_id)


def svc_fact_helper_validate_and_get_team(team_id: uuid.UUID):
    return svc_game_get_team_by_id(team_id)


def svc_fact_helper_validate_and_get_fact_by_id(fact_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    try:
        return None, Fact.objects.get(external_id=fact_id)
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.INVALID_FACT_ID, fact_id=fact_id), None


def svc_fact_helper_create_fact(fact_type: FactType, game: Game, target_team: Team, fact_info: dict) -> Fact:
    logger.debug(f">> ARGS: {locals()}")

    try:
        fact_info = FactMetaConfig.from_json(fact_info)
    except KeyError as e:
        return ErrorCode(ErrorCode.INVALID_FACT_INFO, error=repr(e)), None

    fact = Fact.create(fact_type=fact_type, game=game, target_team=target_team, fact_info=fact_info)

    return None, fact


def svc_fact_helper_get_serialized_facts(facts: Fact | list[Fact], many: bool):
    logger.debug(f">> ARGS: {locals()}")

    return FactSerializer(facts, many=many).data


def svc_fact_helper_get_facts(game: Game, request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    facts = Fact.objects.filter(game=game)

    error, facts = svc_fact_helper_apply_filters_for_fact(request_data, facts)
    if error:
        return error, None

    facts = facts.order_by("created")

    return None, facts


def svc_fact_helper_update_fact(fact: Fact, fact_info: dict):
    logger.debug(f">> ARGS: {locals()}")

    try:
        fact_info = FactMetaConfig.from_json(fact_info)
    except KeyError as e:
        return ErrorCode(ErrorCode.INVALID_FACT_INFO, error=repr(e)), None

    fact.set_fact_info(fact_info, save=True)

    return None, fact


def svc_fact_helper_delete_fact(fact: Fact):
    logger.debug(f">> ARGS: {locals()}")

    fact.is_deleted = True
    fact.save()

    return fact
