import logging
import uuid

from common.constants import AnswerInstructionType, QuestionRewardType, UserRolesType
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
from game.models import Game, Team
from game.services.interfacer import (
    svc_game_get_game_by_id,
    svc_game_get_team_by_id,
    svc_game_verify_player_belongs_to_game,
    svc_game_verify_player_belongs_to_team,
)
from profile_player.models import PlayerProfile
from qna.api.serializers import (
    AskedQuestionDetailSerializer,
    QuestionCategorySerializer,
    QuestionDetailSerializer,
    QuestionRewardSerializer,
    QuestionSerializer,
)
from qna.models import (
    AskedQuestion,
    GameQuestion,
    Placeholder,
    PlaceholderAllowedValue,
    QuestionCategory,
    QuestionReward,
    QuestionTemplate,
)
from qna.popo.answer_meta.answer import AnswerConfig
from qna.popo.instruction_meta import AnswerInstructionMeta
from qna.popo.question_meta.question import QuestionMetaConfig
from qna.popo.question_meta_type.geo_count import GeoCountConfig
from qna.popo.reward_meta.reward_types_map import REWARD_TYPE_MAP

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


def _apply_filters_to_rewards(rewards: list[QuestionReward], request_data: dict) -> list[QuestionReward]:
    logger.debug(f">> ARGS: {locals()}")

    if request_data.get("reward_type"):
        rewards = rewards.filter(
            reward_type=QuestionRewardType.tokentype_from_string(request_data["reward_type"]).value
        )

    return rewards


def _apply_filters_to_asked_questions(asked_questions: list[AskedQuestion], request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if "target_team_id" in request_data:
        asked_questions = asked_questions.filter(target__external_id=request_data["target_team_id"])

    return asked_questions


def svc_qna_helper_run_validations_to_get_rewards(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if request_data.get("reward_type"):
        try:
            QuestionRewardType.tokentype_from_string(request_data["reward_type"])
        except KeyError:
            return ErrorCode(ErrorCode.INVALID_REWARD_TYPE, reward_type=request_data["reward_type"])

    return None


def svc_qna_helper_run_validations_to_create_reward(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("reward_name"):
        return ErrorCode(ErrorCode.MISSING_REWARD_NAME)

    if not request_data.get("reward_type"):
        return ErrorCode(ErrorCode.MISSING_REWARD_TYPE)

    if not request_data.get("reward_meta"):
        return ErrorCode(ErrorCode.MISSING_REWARD_META)

    try:
        QuestionRewardType.tokentype_from_string(request_data["reward_type"])
    except KeyError:
        return ErrorCode(ErrorCode.INVALID_REWARD_TYPE, reward_type=request_data["reward_type"])

    try:
        reward_meta = REWARD_TYPE_MAP[QuestionRewardType.tokentype_from_string(request_data["reward_type"])].from_json(
            request_data["reward_meta"]
        )
    except KeyError:
        return ErrorCode(ErrorCode.INVALID_REWARD_META, reward_meta=request_data["reward_meta"])

    return None


def svc_qna_helper_run_validations_to_create_category(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("category_name"):
        return ErrorCode(ErrorCode.MISSING_CATEGORY_NAME)

    if not request_data.get("reward_id"):
        return ErrorCode(ErrorCode.MISSING_REWARD_ID)

    if not request_data.get("priority"):
        return ErrorCode(ErrorCode.MISSING_PRIORITY)

    return None


def svc_qna_helper_run_validations_to_create_question(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("template"):
        return ErrorCode(ErrorCode.MISSING_TEMPLATE)

    if not request_data.get("placeholders"):
        return ErrorCode(ErrorCode.MISSING_PLACEHOLDERS)

    if not request_data.get("answer_instruction_type"):
        return ErrorCode(ErrorCode.MISSING_ANSWER_INSTRUCTION_TYPE)

    return None


def svc_qna_helper_run_validations_to_assign_question_to_game(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("question_ids"):
        return ErrorCode(ErrorCode.MISSING_QUESTION_IDS)

    extracted_ids = QuestionTemplate.objects.filter(external_id__in=request_data["question_ids"]).values_list(
        "external_id", flat=True
    )
    missing_ids = set(str(question_id) for question_id in request_data["question_ids"]) - set(
        str(question_id) for question_id in extracted_ids
    )
    if missing_ids:
        return ErrorCode(ErrorCode.INVALID_QUESTION_IDS, invalid_question_ids=list(missing_ids))

    return None


def svc_qna_helper_run_validations_to_ask_question(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("target_team_id"):
        return ErrorCode(ErrorCode.MISSING_TARGET_TEAM_ID)

    if not request_data.get("chosen_placeholders"):
        return ErrorCode(ErrorCode.MISSING_CHOSEN_PLACEHOLDERS)

    if not request_data.get("question_meta"):
        return ErrorCode(ErrorCode.MISSING_QUESTION_META)

    return None


def svc_qna_helper_run_validations_to_update_asked_question(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("question_meta"):
        return ErrorCode(ErrorCode.MISSING_QUESTION_META)

    return None


def svc_qna_helper_run_validations_to_get_questions_for_category_player(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("game_id"):
        return ErrorCode(ErrorCode.MISSING_GAME_ID)

    return None


def svc_qna_helper_run_validations_to_answer_asked_question(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("answer_meta"):
        return ErrorCode(ErrorCode.MISSING_ANSWER_META)

    return None


def svc_qna_helper_verify_player_belongs_to_team(player: PlayerProfile, team: Team):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_game_verify_player_belongs_to_team(player, team)
    if error:
        return error

    return None


def svc_qna_helper_verify_player_belongs_to_game(player: PlayerProfile, game: Game):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_game_verify_player_belongs_to_game(player, game)
    if error:
        return error

    return None


def svc_qna_helper_validate_and_get_game(game_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_get_game_by_id(game_id=game_id)


def svc_qna_helper_validate_and_get_team(team_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_get_team_by_id(team_id=team_id)


def svc_qna_helper_get_category_by_id(category_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    try:
        category = QuestionCategory.objects.get(external_id=category_id)
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.INVALID_CATEGORY_ID, category_id=category_id), None

    return None, category


def svc_qna_helper_get_question_for_category_by_id(category: QuestionCategory, question_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    try:
        question = QuestionTemplate.objects.get(category=category, external_id=question_id)
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.INVALID_QUESTION_ID, question_id=question_id), None

    return None, question


def svc_qna_helper_get_question_by_id(question_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    try:
        question = QuestionTemplate.objects.get(external_id=question_id)
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.INVALID_QUESTION_ID, question_id=question_id), None

    return None, question


def svc_qna_helper_get_reward_by_id(reward_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    try:
        reward = QuestionReward.objects.get(external_id=reward_id)
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.INVALID_REWARD_ID, reward_id=reward_id), None

    return None, reward


def svc_qna_helper_validate_and_get_game_question(game: Game, question: QuestionTemplate):
    logger.debug(f">> ARGS: {locals()}")

    try:
        game_question = GameQuestion.objects.get(game=game, question_template=question)
    except ObjectDoesNotExist:
        return (
            ErrorCode(
                ErrorCode.QUESTION_NOT_ASSIGNED_TO_GAME,
                game_id=str(game.get_external_id()),
                question_id=str(question.get_external_id()),
            ),
            None,
        )

    return None, game_question


def svc_qna_helper_validate_and_get_asked_question(asked_question_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    try:
        asked_question = AskedQuestion.objects.get(external_id=asked_question_id)
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.INVALID_QUESTION_ID, question_id=asked_question_id), None

    return None, asked_question


def svc_qna_helper_get_rewards(request_data: dict) -> list[QuestionReward]:
    logger.debug(f">> ARGS: {locals()}")

    rewards = QuestionReward.objects.all()
    rewards = _apply_filters_to_rewards(rewards=rewards, request_data=request_data)
    rewards = rewards.order_by("created")
    return rewards


def svc_qna_helper_get_serialized_rewards(
    rewards: QuestionReward | list[QuestionReward], many: bool
) -> dict | list[dict]:
    logger.debug(f">> ARGS: {locals()}")

    return QuestionRewardSerializer(rewards, many=many).data


def svc_qna_helper_create_reward(
    reward_name: str, reward_type: QuestionRewardType, reward_meta: dict
) -> QuestionReward:
    logger.debug(f">> ARGS: {locals()}")
    reward_meta_popo = REWARD_TYPE_MAP[reward_type].from_json(reward_meta)
    return QuestionReward.create(reward_name=reward_name, reward_type=reward_type, reward_meta=reward_meta_popo)


def svc_qna_helper_get_categories():
    logger.debug(f">> ARGS: {locals()}")

    return QuestionCategory.objects.all().order_by("-priority")


def svc_qna_helper_get_serialized_categories(
    categories: QuestionCategory | list[QuestionCategory], many: bool
) -> dict | list[dict]:
    logger.debug(f">> ARGS: {locals()}")

    return QuestionCategorySerializer(categories, many=many).data


def svc_qna_helper_create_category(category_name: str, reward: QuestionReward, priority: int) -> QuestionCategory:
    logger.debug(f">> ARGS: {locals()}")

    return QuestionCategory.create(category_name=category_name, reward=reward, priority=priority)


def svc_qna_helper_get_questions_for_category(
    category: QuestionCategory, role: UserRolesType, game: Game = None
) -> list[QuestionTemplate]:
    logger.debug(f">> ARGS: {locals()}")

    if game:
        question_ids = game.questions.filter(question_template__category=category).values_list(
            "question_template", flat=True
        )
        return QuestionTemplate.objects.filter(pk__in=question_ids).order_by("created")
    else:
        return QuestionTemplate.objects.filter(category=category).order_by("created")


def svc_qna_helper_create_question(
    template: str,
    placeholders: dict[str, dict],
    category: QuestionCategory,
    answer_instruction_type: str,
    geo: dict,
) -> QuestionTemplate:
    logger.debug(f">> ARGS: {locals()}")

    try:
        geo = GeoCountConfig.from_json(geo)
    except KeyError as e:
        return ErrorCode(ErrorCode.INVALID_GEO_COUNT, error=repr(e)), None

    try:
        answer_instruction_type = AnswerInstructionType.tokentype_from_string(answer_instruction_type)
    except KeyError as e:
        return (
            ErrorCode(ErrorCode.INVALID_ANSWER_INSTRUCTION_TYPE, answer_instruction_type=answer_instruction_type),
            None,
        )

    question_template = QuestionTemplate.create(
        template=template, category=category, answer_instruction_type=answer_instruction_type, geo_count=geo
    )

    for key, value in placeholders.items():
        placeholder = Placeholder.create(question=question_template, placeholder_name=key, required=value["required"])
        if value.get("allowed_values"):
            for allowed_value in value["allowed_values"]:
                PlaceholderAllowedValue.create(placeholder=placeholder, value=allowed_value)

    return question_template


def svc_qna_helper_get_serialized_questions(
    questions: QuestionTemplate | list[QuestionTemplate], many: bool
) -> dict | list[dict]:
    logger.debug(f">> ARGS: {locals()}")

    if many:
        return QuestionSerializer(questions, many=True).data

    return QuestionDetailSerializer(questions, many=False).data


def svc_qna_helper_assign_question_to_game(game: Game, question_ids: list[str]):
    logger.debug(f">> ARGS: {locals()}")

    with transaction.atomic():
        for question_id in question_ids:
            question = QuestionTemplate.objects.get(external_id=question_id)
            try:
                GameQuestion.create(question_template=question, game=game)
            except IntegrityError:
                continue

    return None


def svc_qna_helper_ask_question(
    game_question: GameQuestion, target: Team, chosen_placeholders: dict, request_data: dict
):
    logger.debug(f">> ARGS: {locals()}")

    try:
        question_meta = QuestionMetaConfig.from_json(request_data["question_meta"])
    except KeyError as e:
        return ErrorCode(ErrorCode.INVALID_QUESTION_META, error=repr(e)), None

    try:
        fact_meta = AnswerInstructionMeta.from_json(request_data.get("fact_meta", {}))
    except KeyError as e:
        return ErrorCode(ErrorCode.INVALID_FACT_META, error=repr(e)), None

    try:
        asked_question = AskedQuestion.create(
            game_question=game_question,
            target=target,
            chosen_placeholders=chosen_placeholders,
            question_meta=question_meta,
            fact_meta=fact_meta,
        )
    except ValueError as e:
        return ErrorCode(ErrorCode.INVALID_CHOSEN_PLACEHOLDERS, error=str(e)), None

    return None, asked_question


def svc_qna_helper_update_asked_question(asked_question: AskedQuestion, request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if asked_question.answered:
        return ErrorCode(ErrorCode.QUESTION_ALREADY_ANSWERED), None

    try:
        question_meta = QuestionMetaConfig.from_json(request_data["question_meta"])
    except KeyError as e:
        return ErrorCode(ErrorCode.INVALID_QUESTION_META, error=repr(e)), None

    asked_question.set_question_meta(question_meta)

    try:
        fact_meta = AnswerInstructionMeta.from_json(request_data["fact_meta"])
    except KeyError as e:
        return ErrorCode(ErrorCode.INVALID_FACT_META, error=repr(e)), None

    asked_question.set_fact_meta(fact_meta)

    asked_question.save()

    return None, asked_question


def svc_qna_helper_get_serialized_asked_questions(
    asked_questions: AskedQuestion | list[AskedQuestion], many: bool
) -> dict | list[dict]:
    logger.debug(f">> ARGS: {locals()}")

    return AskedQuestionDetailSerializer(asked_questions, many=many).data


def svc_qna_helper_get_asked_questions_for_game(game: Game, request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    asked_questions = AskedQuestion.objects.filter(game_question__game=game).order_by("created")
    asked_questions = _apply_filters_to_asked_questions(asked_questions, request_data)

    return asked_questions


def svc_qna_helper_answer_asked_question(asked_question: AskedQuestion, answer_meta: dict):
    logger.debug(f">> ARGS: {locals()}")

    if asked_question.accepted:
        return ErrorCode(ErrorCode.QUESTION_ANSWER_ALREADY_ACCEPTED), None

    try:
        answer_meta = AnswerConfig.from_json(answer_meta)
    except KeyError as e:
        return ErrorCode(ErrorCode.INVALID_ANSWER_META, error=repr(e)), None

    asked_question.answered = True

    asked_question.set_answer_meta(answer_meta, save=True)

    return None, asked_question


def svc_qna_helper_accept_answered_question(asked_question: AskedQuestion):
    logger.debug(f">> ARGS: {locals()}")

    if not asked_question.answered:
        return ErrorCode(ErrorCode.QUESTION_ANSWER_NOT_ANSWERED), None

    if asked_question.accepted:
        return ErrorCode(ErrorCode.QUESTION_ANSWER_ALREADY_ACCEPTED), None

    asked_question.accepted = True

    asked_question.save()

    return None, asked_question
