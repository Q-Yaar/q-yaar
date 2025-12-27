import logging
import uuid


from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_paginated_response, get_standard_response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from qna.api.serializers import QuestionRewardSerializer
from qna.services.core import svc_qna_create_reward, svc_qna_get_rewards


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
