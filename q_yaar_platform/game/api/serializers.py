from common.constants import GameStatus, GameType
from game.models import Game
from profile_player.api.serializers import PlayerProfileSerializer
from rest_framework import serializers


class GameSerializer(serializers.ModelSerializer):
    game_id = serializers.SerializerMethodField()
    game_type = serializers.SerializerMethodField()
    game_status = serializers.SerializerMethodField()
    game_master = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()
    teams_info = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = (
            "game_id",
            "game_code",
            "game_type",
            "name",
            "description",
            "game_status",
            "game_master",
            "players",
            "teams_info",
            "created",
            "modified",
        )

    def get_game_id(self, obj: Game) -> str:
        return str(obj.get_external_id())

    def get_game_type(self, obj: Game) -> str:
        return GameType.get_string_for_type(GameType(obj.game_type))

    def get_game_status(self, obj: Game) -> str:
        return GameStatus.get_string_for_type(GameStatus(obj.game_status))

    def get_game_master(self, obj: Game) -> dict:
        return obj.get_game_master_info().to_json()

    def get_players(self, obj: Game) -> list[dict]:
        return [PlayerProfileSerializer(player, many=False).data for player in obj.players.all()]

    def get_teams_info(self, obj: Game) -> list[dict]:
        return obj.get_teams_info().to_json()
