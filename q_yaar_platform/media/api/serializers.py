from rest_framework import serializers

from common.constants import AssetStatus, UserRolesType
from media.models import Asset
from profile_game_master.api.serializers import GameMasterProfileSerializer
from profile_player.api.serializers import PlayerProfileSerializer


class AssetSerializer(serializers.ModelSerializer):
    asset_id = serializers.SerializerMethodField()
    game_id = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = (
            "asset_id",
            "game_id",
            "role",
            "object_key",
            "asset_name",
            "content_type",
            "status",
            "created",
            "modified",
        )

    def get_asset_id(self, obj: Asset) -> str:
        return str(obj.get_external_id())

    def get_game_id(self, obj: Asset) -> str:
        return str(obj.game.external_id)

    def get_role(self, obj: Asset) -> dict:
        # The profile is resolved by the service layer and stashed on the
        # asset as _uploader_profile. Returns the full profile data (which
        # nests user_profile.user_id) instead of a bare role string.
        profile = obj._uploader_profile

        if UserRolesType(obj.role) == UserRolesType.PLAYER:
            return PlayerProfileSerializer(profile, many=False).data
        return GameMasterProfileSerializer(profile, many=False).data

    def get_status(self, obj: Asset) -> str:
        return AssetStatus.get_string_for_type(AssetStatus(obj.status))
