from common.constants import LocationClientType
from game.api.serializers import GameSerializer
from live_location.models import LiveLocation, LocationSharingSetting
from profile_player.api.serializers import PlayerProfileSerializer
from rest_framework import serializers


class LiveLocationSerializer(serializers.ModelSerializer):
    player = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    location_pnt = serializers.SerializerMethodField()

    class Meta:
        model = LiveLocation
        fields = (
            "player",
            "client",
            "accuracy",
            "location_pnt",
            "created",
            "modified",
        )

    def get_player(self, obj: LiveLocation) -> str:
        return PlayerProfileSerializer(obj.player, many=False).data

    def get_client(self, obj: LiveLocation) -> str:
        return LocationClientType.get_string_for_type(LocationClientType(obj.client))

    def get_location_pnt(self, obj: LiveLocation) -> str:
        return obj.get_location_point_dict()


class LocationSettingsSerializer(serializers.ModelSerializer):
    tracking_id = serializers.SerializerMethodField()
    player = serializers.SerializerMethodField()
    tracking_endpoint = serializers.SerializerMethodField()

    class Meta:
        model = LocationSharingSetting
        fields = ("tracking_id", "player", "is_sharing_enabled", "tracking_endpoint", "created", "modified")

    def get_tracking_id(self, obj: LocationSharingSetting) -> str:
        return str(obj.get_external_id())

    def get_player(self, obj: LocationSharingSetting) -> str:
        return PlayerProfileSerializer(obj.player, many=False).data

    def get_tracking_endpoint(self, obj: LocationSharingSetting) -> str:
        return f"/wh/v1/live-location/<location_client>/track/{str(obj.get_external_id())}"
