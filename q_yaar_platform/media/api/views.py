import logging
import uuid

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_paginated_response, get_standard_response
from media.api.serializers import AssetSerializer
from media.services.core import (
    svc_media_confirm_upload,
    svc_media_get_assets,
    svc_media_get_download_url,
    svc_media_request_upload,
)


class AssetListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".AssetListView")
    permission_classes = (IsAuthenticated,)
    serializer_class = AssetSerializer

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER, UserRolesType.PLAYER])
    def get(self, request, **kwargs):
        error, assets = svc_media_get_assets(request.query_params)
        return get_paginated_response(self, error, assets, AssetSerializer)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER, UserRolesType.PLAYER])
    def post(self, request, **kwargs):
        error, response = svc_media_request_upload(request.data, request.user, kwargs["role"])
        return get_standard_response(error, response)


class AssetDetailView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".AssetDetailView")
    permission_classes = (IsAuthenticated,)
    serializer_class = AssetSerializer

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER, UserRolesType.PLAYER])
    def get(self, request, asset_id: uuid.UUID, **kwargs):
        error, response = svc_media_get_download_url(asset_id)
        return get_standard_response(error, response)


class AssetConfirmView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".AssetConfirmView")
    permission_classes = (IsAuthenticated,)
    serializer_class = AssetSerializer

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.GAME_MASTER, UserRolesType.PLAYER])
    def patch(self, request, asset_id: uuid.UUID, **kwargs):
        error, response = svc_media_confirm_upload(asset_id)
        return get_standard_response(error, response)
