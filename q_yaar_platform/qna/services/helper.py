import logging
import uuid

from common.constants import QuestionRewardType
from django.core.exceptions import ObjectDoesNotExist
from qna.api.serializers import QuestionCategorySerializer, QuestionRewardSerializer
from qna.models import QuestionCategory, QuestionReward
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


def svc_qna_helper_get_reward_by_id(reward_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    try:
        reward = QuestionReward.objects.get(external_id=reward_id)
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.INVALID_REWARD_ID, reward_id=reward_id), None

    return None, reward


def svc_qna_helper_get_rewards(request_data: dict) -> list[QuestionReward]:
    logger.debug(f">> ARGS: {locals()}")

    rewards = QuestionReward.objects.all()
    rewards = _apply_filters_to_rewards(rewards=rewards, request_data=request_data)
    rewards = rewards.order_by("created")
    return rewards


def svc_qna_helper_get_serialized_rewards(rewards: QuestionReward | list[QuestionReward], many: bool) -> list[dict]:
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

    return QuestionCategory.objects.all().order_by("priority")


def svc_qna_helper_get_serialized_categories(
    categories: QuestionCategory | list[QuestionCategory], many: bool
) -> list[dict]:
    logger.debug(f">> ARGS: {locals()}")

    return QuestionCategorySerializer(categories, many=many).data


def svc_qna_helper_create_category(category_name: str, reward: QuestionReward, priority: int) -> QuestionCategory:
    logger.debug(f">> ARGS: {locals()}")

    return QuestionCategory.create(category_name=category_name, reward=reward, priority=priority)
