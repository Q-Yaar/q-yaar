import logging
import uuid

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.constants import UserRolesType
from common.decorators import validate_profile
from common.response import get_paginated_response, get_standard_response
from media.api.serializers import PROFILE_CONTEXT_KEY, AssetSerializer
from media.services.core import (
    svc_media_confirm_upload,
    svc_media_delete_asset,
    svc_media_get_assets,
    svc_media_get_download_url,
    svc_media_request_upload,
)


class AssetListView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".AssetListView")
    permission_classes = (IsAuthenticated,)
    serializer_class = AssetSerializer

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER, UserRolesType.GAME_MASTER])
    def get(self, request, **kwargs):
        # Unserialized queryset: pagination + serialization happen in
        # get_paginated_response, which needs the profile via context.
        error, assets = svc_media_get_assets(kwargs["profile"], serialized=False)
        return get_paginated_response(
            self, error, assets, AssetSerializer, context={PROFILE_CONTEXT_KEY: kwargs["profile"]}
        )

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER, UserRolesType.GAME_MASTER])
    def post(self, request, **kwargs):
        error, response = svc_media_request_upload(request.data, kwargs["profile"])
        return get_standard_response(error, response)


class AssetDetailView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".AssetDetailView")
    permission_classes = (IsAuthenticated,)
    serializer_class = AssetSerializer

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER, UserRolesType.GAME_MASTER])
    def get(self, request, asset_id: uuid.UUID, **kwargs):
        error, response = svc_media_get_download_url(asset_id, kwargs["profile"])
        return get_standard_response(error, response)

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER, UserRolesType.GAME_MASTER])
    def delete(self, request, asset_id: uuid.UUID, **kwargs):
        error, response = svc_media_delete_asset(asset_id, kwargs["profile"])
        return get_standard_response(error, response)


class AssetConfirmView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".AssetConfirmView")
    permission_classes = (IsAuthenticated,)
    serializer_class = AssetSerializer

    @validate_profile(logger=logger, allowed_roles=[UserRolesType.PLAYER, UserRolesType.GAME_MASTER])
    def patch(self, request, asset_id: uuid.UUID, **kwargs):
        error, response = svc_media_confirm_upload(asset_id, kwargs["profile"])
        return get_standard_response(error, response)
