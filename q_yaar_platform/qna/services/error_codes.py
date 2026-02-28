import logging

from common.base_error_codes import BaseErrorCode
from common.constants import ModuleErrorPrefix
from rest_framework import status

logger = logging.getLogger(__name__)


class ErrorCode(BaseErrorCode):
    # Value Errors - 0 Series
    MISSING_REWARD_NAME = "001"
    MISSING_REWARD_TYPE = "002"
    MISSING_REWARD_META = "003"
    INVALID_REWARD_META = "004"
    MISSING_CATEGORY_NAME = "005"
    MISSING_REWARD_ID = "006"
    MISSING_PRIORITY = "007"
    MISSING_TEMPLATE = "008"
    MISSING_PLACEHOLDERS = "009"
    MISSING_QUESTION_IDS = "010"
    MISSING_GAME_ID = "011"
    MISSING_TARGET_TEAM_ID = "012"
    MISSING_CHOSEN_PLACEHOLDERS = "013"
    MISSING_QUESTION_META = "014"
    MISSING_ANSWER_META = "015"
    MISSING_ANSWER_INSTRUCTION_TYPE = "016"

    # Permission Errors - 1 Series
    QUESTION_ANSWER_ALREADY_ACCEPTED = "101"
    ASSIGNEE_CANNOT_ACCEPT_ANSWER = "102"
    QUESTION_ANSWER_NOT_ANSWERED = "103"
    QUESTION_ALREADY_ANSWERED = "104"
    ASSIGNEE_CANNOT_UPDATE_QUESTION = "105"

    # Key Errors - 2 Series
    INVALID_REWARD_TYPE = "201"
    INVALID_QUESTION_META = "202"
    INVALID_ANSWER_META = "203"
    INVALID_GEO_COUNT = "204"
    INVALID_ANSWER_INSTRUCTION_TYPE = "205"
    INVALID_FACT_META = "206"

    # Object Does Not Exist Errors - 3 series
    INVALID_REWARD_ID = "301"
    INVALID_CATEGORY_ID = "302"
    INVALID_QUESTION_ID = "303"
    INVALID_QUESTION_IDS = "304"
    INVALID_CHOSEN_PLACEHOLDERS = "305"
    QUESTION_NOT_ASSIGNED_TO_GAME = "306"

    # Integrity Errors - 4 Series

    ERROR_CODE_HTTP_MAP = {
        MISSING_REWARD_NAME: status.HTTP_400_BAD_REQUEST,
        MISSING_REWARD_TYPE: status.HTTP_400_BAD_REQUEST,
        MISSING_REWARD_META: status.HTTP_400_BAD_REQUEST,
        INVALID_REWARD_META: status.HTTP_400_BAD_REQUEST,
        MISSING_CATEGORY_NAME: status.HTTP_400_BAD_REQUEST,
        MISSING_REWARD_ID: status.HTTP_400_BAD_REQUEST,
        MISSING_PRIORITY: status.HTTP_400_BAD_REQUEST,
        MISSING_TEMPLATE: status.HTTP_400_BAD_REQUEST,
        MISSING_PLACEHOLDERS: status.HTTP_400_BAD_REQUEST,
        MISSING_QUESTION_IDS: status.HTTP_400_BAD_REQUEST,
        MISSING_GAME_ID: status.HTTP_400_BAD_REQUEST,
        MISSING_TARGET_TEAM_ID: status.HTTP_400_BAD_REQUEST,
        MISSING_CHOSEN_PLACEHOLDERS: status.HTTP_400_BAD_REQUEST,
        MISSING_QUESTION_META: status.HTTP_400_BAD_REQUEST,
        MISSING_ANSWER_META: status.HTTP_400_BAD_REQUEST,
        MISSING_ANSWER_INSTRUCTION_TYPE: status.HTTP_400_BAD_REQUEST,
        QUESTION_ANSWER_ALREADY_ACCEPTED: status.HTTP_400_BAD_REQUEST,
        ASSIGNEE_CANNOT_ACCEPT_ANSWER: status.HTTP_400_BAD_REQUEST,
        QUESTION_ANSWER_NOT_ANSWERED: status.HTTP_400_BAD_REQUEST,
        QUESTION_ALREADY_ANSWERED: status.HTTP_400_BAD_REQUEST,
        ASSIGNEE_CANNOT_UPDATE_QUESTION: status.HTTP_400_BAD_REQUEST,
        INVALID_REWARD_TYPE: status.HTTP_400_BAD_REQUEST,
        INVALID_QUESTION_META: status.HTTP_400_BAD_REQUEST,
        INVALID_ANSWER_META: status.HTTP_400_BAD_REQUEST,
        INVALID_GEO_COUNT: status.HTTP_400_BAD_REQUEST,
        INVALID_ANSWER_INSTRUCTION_TYPE: status.HTTP_400_BAD_REQUEST,
        INVALID_FACT_META: status.HTTP_400_BAD_REQUEST,
        INVALID_REWARD_ID: status.HTTP_400_BAD_REQUEST,
        INVALID_CATEGORY_ID: status.HTTP_400_BAD_REQUEST,
        INVALID_QUESTION_ID: status.HTTP_400_BAD_REQUEST,
        INVALID_QUESTION_IDS: status.HTTP_400_BAD_REQUEST,
        INVALID_CHOSEN_PLACEHOLDERS: status.HTTP_400_BAD_REQUEST,
        QUESTION_NOT_ASSIGNED_TO_GAME: status.HTTP_400_BAD_REQUEST,
    }

    def get_string_for_missing_reward_name(kwargs: dict):
        return "Missing reward_name"

    def get_string_for_missing_reward_type(kwargs: dict):
        return "Missing reward_type"

    def get_string_for_missing_reward_meta(kwargs: dict):
        return "Missing reward_meta"

    def get_string_for_invalid_reward_meta(kwargs: dict):
        return f"Invalid reward_meta: {kwargs.get('reward_meta')}"

    def get_string_for_missing_category_name(kwargs: dict):
        return "Missing category_name"

    def get_string_for_missing_reward_id(kwargs: dict):
        return "Missing reward_id"

    def get_string_for_missing_priority(kwargs: dict):
        return "Missing priority"

    def get_string_for_missing_template(kwargs: dict):
        return "Missing template"

    def get_string_for_missing_placeholders(kwargs: dict):
        return "Missing placeholders"

    def get_string_for_missing_question_ids(kwargs: dict):
        return "Missing question_ids"

    def get_string_for_missing_game_id(kwargs: dict):
        return "Missing game_id"

    def get_string_for_missing_target_team_id(kwargs: dict):
        return "Missing target_team_id"

    def get_string_for_missing_chosen_placeholders(kwargs: dict):
        return "Missing chosen_placeholders"

    def get_string_for_missing_question_meta(kwargs: dict):
        return "Missing question_meta"

    def get_string_for_missing_answer_meta(kwargs: dict):
        return "Missing answer_meta"

    def get_string_for_missing_answer_instruction_type(kwargs: dict):
        return "Missing answer_instruction_type"

    def get_string_for_question_answer_already_accepted(kwargs: dict):
        return "Question cannot be answered after it is accepted"

    def get_string_for_assignee_cannot_accept_answer(kwargs: dict):
        return "Assignee cannot accept their own answer"

    def get_string_for_question_answer_not_answered(kwargs: dict):
        return "Question is not answered yet"

    def get_string_for_question_already_answered(kwargs: dict):
        return "Question is already answered"

    def get_string_for_assignee_cannot_update_question(kwargs: dict):
        return "Assignee cannot update the question"

    def get_string_for_invalid_reward_type(kwargs: dict):
        return f"Invalid reward_type: {kwargs.get('reward_type')}"

    def get_string_for_invalid_question_meta(kwargs: dict):
        return f"Invalid question_meta: {kwargs.get('error')}"

    def get_string_for_invalid_answer_meta(kwargs: dict):
        return f"Invalid answer_meta: {kwargs.get('error')}"

    def get_string_for_invalid_geo_count(kwargs: dict):
        return f"Invalid geo_count: {kwargs.get('error')}"

    def get_string_for_invalid_answer_instruction_type(kwargs: dict):
        return f"Invalid answer_instruction_type: {kwargs.get('answer_instruction_type')}"

    def get_string_for_invalid_fact_meta(kwargs: dict):
        return f"Invalid fact_meta: {kwargs.get('error')}"

    def get_string_for_invalid_reward_id(kwargs: dict):
        return f"Invalid reward_id: {kwargs.get('reward_id')}"

    def get_string_for_invalid_category_id(kwargs: dict):
        return f"Invalid category_id: {kwargs.get('category_id')}"

    def get_string_for_invalid_question_id(kwargs: dict):
        return f"Invalid question_id: {kwargs.get('question_id')}"

    def get_string_for_invalid_question_ids(kwargs: dict):
        return f"Invalid question_ids: {kwargs.get('question_ids')}"

    def get_string_for_invalid_chosen_placeholders(kwargs: dict):
        return f"Invalid chosen_placeholders: {kwargs.get('error')}"

    def get_string_for_question_not_assigned_to_game(kwargs: dict):
        return f"Question {kwargs.get('question_id')} is not assigned to game {kwargs.get('game_id')}"

    CODE_MESSAGE_MAP = {
        MISSING_REWARD_NAME: get_string_for_missing_reward_name,
        MISSING_REWARD_TYPE: get_string_for_missing_reward_type,
        MISSING_REWARD_META: get_string_for_missing_reward_meta,
        INVALID_REWARD_META: get_string_for_invalid_reward_meta,
        MISSING_CATEGORY_NAME: get_string_for_missing_category_name,
        MISSING_REWARD_ID: get_string_for_missing_reward_id,
        MISSING_PRIORITY: get_string_for_missing_priority,
        MISSING_TEMPLATE: get_string_for_missing_template,
        MISSING_PLACEHOLDERS: get_string_for_missing_placeholders,
        MISSING_QUESTION_IDS: get_string_for_missing_question_ids,
        MISSING_GAME_ID: get_string_for_missing_game_id,
        MISSING_TARGET_TEAM_ID: get_string_for_missing_target_team_id,
        MISSING_CHOSEN_PLACEHOLDERS: get_string_for_missing_chosen_placeholders,
        MISSING_QUESTION_META: get_string_for_missing_question_meta,
        MISSING_ANSWER_META: get_string_for_missing_answer_meta,
        MISSING_ANSWER_INSTRUCTION_TYPE: get_string_for_missing_answer_instruction_type,
        QUESTION_ANSWER_ALREADY_ACCEPTED: get_string_for_question_answer_already_accepted,
        ASSIGNEE_CANNOT_ACCEPT_ANSWER: get_string_for_assignee_cannot_accept_answer,
        QUESTION_ANSWER_NOT_ANSWERED: get_string_for_question_answer_not_answered,
        QUESTION_ALREADY_ANSWERED: get_string_for_question_already_answered,
        ASSIGNEE_CANNOT_UPDATE_QUESTION: get_string_for_assignee_cannot_update_question,
        INVALID_REWARD_TYPE: get_string_for_invalid_reward_type,
        INVALID_QUESTION_META: get_string_for_invalid_question_meta,
        INVALID_ANSWER_META: get_string_for_invalid_answer_meta,
        INVALID_GEO_COUNT: get_string_for_invalid_geo_count,
        INVALID_ANSWER_INSTRUCTION_TYPE: get_string_for_invalid_answer_instruction_type,
        INVALID_FACT_META: get_string_for_invalid_fact_meta,
        INVALID_REWARD_ID: get_string_for_invalid_reward_id,
        INVALID_CATEGORY_ID: get_string_for_invalid_category_id,
        INVALID_QUESTION_ID: get_string_for_invalid_question_id,
        INVALID_QUESTION_IDS: get_string_for_invalid_question_ids,
        INVALID_CHOSEN_PLACEHOLDERS: get_string_for_invalid_chosen_placeholders,
        QUESTION_NOT_ASSIGNED_TO_GAME: get_string_for_question_not_assigned_to_game,
    }

    def __init__(self, code, **kwargs) -> None:
        self.ERROR_CODE_HTTP_MAP.update(super(ErrorCode, self).ERROR_CODE_HTTP_MAP)
        self.CODE_MESSAGE_MAP.update(super(ErrorCode, self).CODE_MESSAGE_MAP)

        (
            logger.debug(f">> ARGS: {locals()}")
            if code in [self.SUCCESS, self.CREATED, self.NO_CONTENT]
            else logger.warning(f"{self.CODE_MESSAGE_MAP[code](kwargs)} - {locals()}")
        )

        super(ErrorCode, self).__init__(
            code,
            self.ERROR_CODE_HTTP_MAP[code],
            self.CODE_MESSAGE_MAP[code](kwargs) if code not in [self.SUCCESS, self.CREATED, self.NO_CONTENT] else None,
            ModuleErrorPrefix.QNA,
        )
