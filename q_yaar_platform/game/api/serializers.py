from common.constants import GameStatus, GameType, GameVisibilityMode, TeamType
from game.models import Game, Team
from profile_player.api.serializers import PlayerProfileSerializer
from profile_player.models import PlayerProfile
from rest_framework import serializers


class GameSerializer(serializers.ModelSerializer):
    game_id = serializers.SerializerMethodField()
    game_type = serializers.SerializerMethodField()
    game_visibility_mode = serializers.SerializerMethodField()
    game_status = serializers.SerializerMethodField()
    game_master = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = (
            "game_id",
            "game_code",
            "game_type",
            "game_visibility_mode",
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

    def get_game_visibility_mode(self, obj: Game) -> str:
        return GameVisibilityMode.get_string_for_type(GameVisibilityMode(obj.game_visibility_mode))

    def get_game_status(self, obj: Game) -> str:
        return GameStatus.get_string_for_type(GameStatus(obj.game_status))

    def get_game_master(self, obj: Game) -> dict:
        return obj.get_game_master_info().to_json()


class GameDetailSerializer(GameSerializer):
    teams = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = GameSerializer.Meta.fields + ("teams",)

    def get_teams(self, obj: Game) -> list[dict]:
        teams = Team.objects.filter(game=obj).order_by("team_type")
        return TeamSerializer(teams, many=True).data


class TeamSerializer(serializers.ModelSerializer):
    team_id = serializers.SerializerMethodField()
    game_id = serializers.SerializerMethodField()
    team_type = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ("team_id", "game_id", "team_name", "team_colour", "team_type", "players", "created", "modified")

    def get_team_id(self, obj: Team) -> str:
        return str(obj.get_external_id())

    def get_game_id(self, obj: Team) -> str:
        return str(obj.game.get_external_id())

    def get_team_type(self, obj: Team) -> str:
        return TeamType.get_string_for_type(TeamType(obj.team_type))

    def get_players(self, obj: Team) -> list[dict]:
        players = PlayerProfile.objects.filter(teamplayerrelation__team=obj)
        result = PlayerProfileSerializer(players, many=True).data
        return result
