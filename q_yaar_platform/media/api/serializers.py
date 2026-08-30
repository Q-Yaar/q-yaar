from rest_framework import serializers

from common.constants import AssetStatus, UserRolesType
from media.models import Asset


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

    def get_role(self, obj: Asset) -> str:
        return UserRolesType.get_string_for_type(UserRolesType(obj.role))

    def get_status(self, obj: Asset) -> str:
        return AssetStatus.get_string_for_type(AssetStatus(obj.status))
