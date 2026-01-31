import logging
import uuid

from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_paginated_response, get_standard_response
from qna.api.serializers import (
    AskedQuestionDetailSerializer,
    QuestionCategorySerializer,
    QuestionRewardSerializer,
    QuestionSerializer,
)
from qna.services.core import (
    svc_qna_answer_asked_question,
    svc_qna_ask_question,
    svc_qna_assign_question_to_game,
    svc_qna_create_cateogory,
    svc_qna_create_question,
    svc_qna_create_reward,
    svc_qna_get_asked_questions_for_game,
    svc_qna_get_categories,
    svc_qna_get_question_by_id,
    svc_qna_get_questions_for_category,
    svc_qna_get_rewards,
)
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class RewardsListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".RewardsListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def get(self, request, **kwargs):
        error, rewards = svc_qna_get_rewards(request.query_params)
        return get_paginated_response(self, error, rewards, QuestionRewardSerializer)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def post(self, request, **kwargs):
        error, response = svc_qna_create_reward(request.data)
        return get_standard_response(error, response)


class CategoriesListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".CategoriesListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER, UserRolesType.PLAYER])
    def get(self, request, **kwargs):
        error, categories = svc_qna_get_categories()
        return get_paginated_response(self, error, categories, QuestionCategorySerializer)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def post(self, request, **kwargs):
        error, response = svc_qna_create_cateogory(request.data)
        return get_standard_response(error, response)


class QuestionListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".QuestionListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER, UserRolesType.PLAYER])
    def get(self, request, category_id: uuid.UUID, **kwargs):
        role = kwargs["role"]
        error, questions = svc_qna_get_questions_for_category(category_id, role, request.query_params)
        return get_paginated_response(self, error, questions, QuestionSerializer)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def post(self, request, category_id: uuid.UUID, **kwargs):
        error, response = svc_qna_create_question(request.data, category_id)
        return get_standard_response(error, response)


class QuestionDetailView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".QuestionDetailView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER, UserRolesType.PLAYER])
    def get(self, request, category_id: uuid.UUID, question_id: uuid.UUID, **kwargs):
        error, response = svc_qna_get_question_by_id(category_id, question_id)
        return get_standard_response(error, response)


class GameQuestionsListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".GameQuestionsListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER])
    def post(self, request, game_id: uuid.UUID, **kwargs):
        error, response = svc_qna_assign_question_to_game(game_id, request.data)
        return get_standard_response(error, response)


class GameAskedQuestionsListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".GameAskedQuestionsListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER, UserRolesType.PLAYER])
    def get(self, request, game_id: uuid.UUID, **kwargs):
        error, questions = svc_qna_get_asked_questions_for_game(game_id, request.query_params)
        return get_paginated_response(self, error, questions, AskedQuestionDetailSerializer)


class GameQuestionsAskView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".GameQuestionsAskView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, game_id: uuid.UUID, question_id: uuid.UUID, **kwargs):
        error, response = svc_qna_ask_question(game_id, question_id, request.data)
        return get_standard_response(error, response)


class GameQuestionsAnswerView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".GameQuestionsAnswerView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def patch(self, request, game_id: uuid.UUID, asked_question_id: uuid.UUID, **kwargs):
        profile = kwargs["profile"]
        error, response = svc_qna_answer_asked_question(asked_question_id, request.data, profile)
        return get_standard_response(error, response)
