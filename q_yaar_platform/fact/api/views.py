import logging
import uuid

from fact.api.serializers import FactSerializer
from fact.services.core import svc_fact_create_fact, svc_fact_delete_fact, svc_fact_get_facts, svc_fact_update_fact
from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_paginated_response, get_standard_response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class FactsListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".FactsListView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def get(self, request, **kwargs):
        error, facts = svc_fact_get_facts(request.query_params)
        return get_paginated_response(self, error, facts, FactSerializer)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def post(self, request, **kwargs):
        error, response = svc_fact_create_fact(request.data)
        return get_standard_response(error, response)


class FactDetailView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".FactDetailView")
    permission_classes = (IsAuthenticated,)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def patch(self, request, fact_id: uuid.UUID, **kwargs):
        error, response = svc_fact_update_fact(fact_id, request.data)
        return get_standard_response(error, response)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER])
    def delete(self, request, fact_id: uuid.UUID, **kwargs):
        error, response = svc_fact_delete_fact(fact_id)
        return get_standard_response(error, response)
