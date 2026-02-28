from rest_framework import serializers

from common.constants import ClientType
from location.models import Location, LocationSharingSetting


class LocationPointSerializer(serializers.Serializer):
    lat = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    lon = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    reported_time = serializers.DateTimeField(required=True)
    accuracy = serializers.FloatField(required=False, allow_null=True)


class LocationCreateSerializer(serializers.Serializer):
    game_id = serializers.UUIDField(required=False, allow_null=True)
    team_id = serializers.UUIDField(required=False, allow_null=True)
    client = serializers.ChoiceField(
        choices=[(item.name, item.value) for item in ClientType],
        required=True
    )
    locations = serializers.ListField(
        child=LocationPointSerializer(), required=True, min_length=1, max_length=100
    )


class LocationResponseSerializer(serializers.ModelSerializer):
    player_id = serializers.UUIDField(source="player.external_id", read_only=True)
    game_id = serializers.UUIDField(source="game.external_id", read_only=True, allow_null=True)
    team_id = serializers.UUIDField(source="team.external_id", read_only=True, allow_null=True)

    class Meta:
        model = Location
        fields = (
            "external_id",
            "player_id",
            "game_id",
            "team_id",
            "lat",
            "lon",
            "accuracy",
            "reported_time",
            "client",
        )
        read_only_fields = fields


class LocationSharingSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationSharingSetting
        fields = ("is_sharing_enabled", "tracking_code")
        read_only_fields = ("tracking_code",)


class LocationTrackingCodeUpdateSerializer(serializers.Serializer):
    # Empty serializer since this will just be a POST/PATCH to generate a new code
    pass
