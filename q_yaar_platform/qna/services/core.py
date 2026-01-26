import logging
import uuid

from common.constants import QuestionRewardType, UserRolesType
from qna.services.helper import (
    svc_qna_helper_assign_question_to_game,
    svc_qna_helper_create_category,
    svc_qna_helper_create_question,
    svc_qna_helper_create_reward,
    svc_qna_helper_get_categories,
    svc_qna_helper_get_category_by_id,
    svc_qna_helper_get_question_by_id,
    svc_qna_helper_get_questions_for_category,
    svc_qna_helper_get_reward_by_id,
    svc_qna_helper_get_rewards,
    svc_qna_helper_get_serialized_categories,
    svc_qna_helper_get_serialized_questions,
    svc_qna_helper_get_serialized_rewards,
    svc_qna_helper_run_validations_to_assign_question_to_game,
    svc_qna_helper_run_validations_to_create_category,
    svc_qna_helper_run_validations_to_create_question,
    svc_qna_helper_run_validations_to_create_reward,
    svc_qna_helper_run_validations_to_get_questions_for_category_player,
    svc_qna_helper_run_validations_to_get_rewards,
    svc_qna_helper_validate_and_get_game,
)

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


def svc_qna_get_rewards(request_data: dict, serialized: bool = False):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_qna_helper_run_validations_to_get_rewards(request_data)
    if error:
        return error, None

    rewards = svc_qna_helper_get_rewards(request_data)

    if serialized:
        rewards = svc_qna_helper_get_serialized_rewards(rewards, many=True)

    return ErrorCode(ErrorCode.SUCCESS), rewards


def svc_qna_create_reward(request_data: dict, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_qna_helper_run_validations_to_create_reward(request_data)
    if error:
        return error, None

    reward = svc_qna_helper_create_reward(
        reward_name=request_data["reward_name"],
        reward_type=QuestionRewardType.tokentype_from_string(request_data["reward_type"]),
        reward_meta=request_data["reward_meta"],
    )

    if serialized:
        reward = svc_qna_helper_get_serialized_rewards(reward, many=False)

    return ErrorCode(ErrorCode.CREATED), reward


def svc_qna_get_categories(serialized: bool = False):
    logger.debug(f">> ARGS: {locals()}")

    categories = svc_qna_helper_get_categories()

    if serialized:
        categories = svc_qna_helper_get_serialized_categories(categories, many=True)

    return ErrorCode(ErrorCode.SUCCESS), categories


def svc_qna_create_cateogory(request_data: dict, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_qna_helper_run_validations_to_create_category(request_data)
    if error:
        return error, None

    error, reward = svc_qna_helper_get_reward_by_id(request_data["reward_id"])
    if error:
        return error, None

    category = svc_qna_helper_create_category(request_data["category_name"], reward, request_data["priority"])

    if serialized:
        category = svc_qna_helper_get_serialized_categories(category, many=False)

    return ErrorCode(ErrorCode.CREATED), category


def svc_qna_get_questions_for_category(
    category_id: uuid.UUID, role: UserRolesType, request_data: dict, serialized: bool = False
):
    logger.debug(f">> ARGS: {locals()}")

    error, category = svc_qna_helper_get_category_by_id(category_id)
    if error:
        return error, None

    game = None

    if role == UserRolesType.PLAYER:
        error = svc_qna_helper_run_validations_to_get_questions_for_category_player(request_data)
        if error:
            return error, None

        error, game = svc_qna_helper_validate_and_get_game(request_data["game_id"])
        if error:
            return error, None
    elif role == UserRolesType.GAME_MASTER and request_data.get("game_id"):
        error, game = svc_qna_helper_validate_and_get_game(request_data["game_id"])
        if error:
            return error, None

    questions = svc_qna_helper_get_questions_for_category(category, role, game=game)

    if serialized:
        questions = svc_qna_helper_get_serialized_questions(questions, many=True)

    return ErrorCode(ErrorCode.SUCCESS), questions


def svc_qna_create_question(request_data: dict, category_id: uuid.UUID, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_qna_helper_run_validations_to_create_question(request_data)
    if error:
        return error, None

    error, category = svc_qna_helper_get_category_by_id(category_id)
    if error:
        return error, None

    question = svc_qna_helper_create_question(request_data["template"], request_data.get("placeholders", {}), category)

    if serialized:
        question = svc_qna_helper_get_serialized_questions(question, many=False)

    return ErrorCode(ErrorCode.CREATED), question


def svc_qna_get_question_by_id(category_id: uuid.UUID, question_id: uuid.UUID, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, category = svc_qna_helper_get_category_by_id(category_id)
    if error:
        return error, None

    error, question = svc_qna_helper_get_question_by_id(category, question_id)
    if error:
        return error, None

    if serialized:
        question = svc_qna_helper_get_serialized_questions(question, many=False)

    return ErrorCode(ErrorCode.SUCCESS), question


def svc_qna_assign_question_to_game(game_id: uuid.UUID, request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_qna_helper_run_validations_to_assign_question_to_game(request_data)
    if error:
        return error, None

    error, game = svc_qna_helper_validate_and_get_game(game_id)
    if error:
        return error, None

    svc_qna_helper_assign_question_to_game(game, request_data["question_ids"])

    return ErrorCode(ErrorCode.NO_CONTENT), None
