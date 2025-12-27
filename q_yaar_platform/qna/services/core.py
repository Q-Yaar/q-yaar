import logging

from common.constants import QuestionRewardType
from qna.services.helper import (
    svc_qna_helper_create_reward,
    svc_qna_helper_get_rewards,
    svc_qna_helper_get_serialized_rewards,
    svc_qna_helper_run_validations_to_create_reward,
    svc_qna_helper_run_validations_to_get_rewards,
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
