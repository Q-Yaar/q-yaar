from common.constants import GameStatus, GameType
from game.models import Game, Team, TeamPlayerRelation
from rest_framework import serializers

from profile_player.api.serializers import PlayerProfileSerializer
from profile_player.models import PlayerProfile


class GameSerializer(serializers.ModelSerializer):
    game_id = serializers.SerializerMethodField()
    game_type = serializers.SerializerMethodField()
    game_status = serializers.SerializerMethodField()
    game_master = serializers.SerializerMethodField()

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


class TeamSerializer(serializers.ModelSerializer):
    game_id = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ("game_id", "team_name", "team_colour", "players", "created", "modified")

    def get_game_id(self, obj: Team) -> str:
        return str(obj.game.get_external_id())

    def get_players(self, obj: Team) -> list[dict]:
        players = PlayerProfile.objects.filter(teamplayerrelation__team=obj)
        result = PlayerProfileSerializer(players, many=True).data
        return result
