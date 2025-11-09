from rest_framework import serializers

from account.api.serializers import PlatformUserSerializer
from profile_game_master.models import GameMasterProfile


class GameMasterProfileSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = GameMasterProfile
        fields = ("profile_name", "user_profile", "profile_pic", "created", "modified", "is_suspended")

    def get_user_profile(self, obj: GameMasterProfile) -> dict:
        return PlatformUserSerializer(obj.platform_user, many=False).data

    def get_profile_pic(self, obj: GameMasterProfile) -> dict:
        return obj.get_profile_pic()
