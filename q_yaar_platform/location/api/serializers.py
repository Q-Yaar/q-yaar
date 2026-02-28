from rest_framework import serializers

from common.constants import LocationClientType
from location.models import Location, LocationSharingSetting


class LocationPointSerializer(serializers.Serializer):
    lat = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    lon = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    timestamp = serializers.DateTimeField(required=True)
    accuracy = serializers.FloatField(required=False, allow_null=True)


class LocationCreateSerializer(serializers.Serializer):
    game_id = serializers.UUIDField(required=False, allow_null=True)
    team_id = serializers.UUIDField(required=False, allow_null=True)
    client = serializers.ChoiceField(
        choices=[(item.name, item.value) for item in LocationClientType],
        required=True
    )
    locations = serializers.ListField(
        child=LocationPointSerializer(), required=True, min_length=1, max_length=100
    )


class LocationResponseSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
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
            "timestamp",
            "client",
        )
        read_only_fields = fields

    def get_client(self, obj) -> str:
        client = obj.get("client") if isinstance(obj, dict) else getattr(obj, "client", getattr(obj, "_client", None))
        try:
            return LocationClientType(client).name
        except ValueError:
            return str(client)


class LocationSharingSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationSharingSetting
        fields = ("is_sharing_enabled", "tracking_code")
        read_only_fields = ("tracking_code",)


class LocationTrackingCodeUpdateSerializer(serializers.Serializer):
    # Empty serializer since this will just be a POST/PATCH to generate a new code
    pass


class WebhookTraccarCoordsSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=12, decimal_places=8, required=True)
    longitude = serializers.DecimalField(max_digits=12, decimal_places=8, required=True)
    accuracy = serializers.FloatField(required=True)


class WebhookTraccarLocationObjectSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField(required=True)
    coords = WebhookTraccarCoordsSerializer(required=True)


class WebhookTraccarLocationSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=64, min_length=1, required=True)
    location = WebhookTraccarLocationObjectSerializer(required=True)

    def validate_device_id(self, value):
        return value.strip()
