from common.abstract_models import AbstractExternalFacing, AbstractTimeStamped
from common.constants import GameStatus, GameType, Length
from django.db import models

from common.uuid import unique_uuid4
from game.popo.game_master_info import GameMasterInfoConfig
from profile_game_master.models import GameMasterProfile
from profile_player.models import PlayerProfile


class Game(AbstractExternalFacing, AbstractTimeStamped):
    CONST_KEY_GAME_MASTER_INFO = "game_master_info"
    CONST_KEY_TEAMS_INFO = "teams_info"

    game_code = models.CharField(max_length=Length.GAME_CODE, unique=True)
    game_type = models.PositiveIntegerField(choices=GameType.get_choices())
    name = models.CharField(max_length=Length.GAME_NAME)
    description = models.TextField()
    game_status = models.PositiveSmallIntegerField(choices=GameStatus.get_choices(), default=GameStatus.PENDING.value)
    created_by = models.ForeignKey(GameMasterProfile, on_delete=models.SET_NULL, blank=True, null=True)

    info = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.game_code

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["game_code"]),
            models.Index(fields=["game_code", "game_status"]),
        ]

    def get_game_master_info(self) -> GameMasterInfoConfig:
        return GameMasterInfoConfig.from_json(self.info.get(self.CONST_KEY_GAME_MASTER_INFO))

    def set_game_master_info(self, config: GameMasterInfoConfig, save: bool = False) -> None:
        info = self.info
        info[self.CONST_KEY_GAME_MASTER_INFO] = config.to_json()
        self.info = info
        if save:
            self.save()

    @classmethod
    def create(
        cls,
        game_type: GameType,
        name: str,
        description: str,
        created_by: GameMasterProfile,
    ) -> "Game":
        game_code = str(unique_uuid4())[:6]
        game = cls(
            game_type=game_type.value, game_code=game_code, name=name, description=description, created_by=created_by
        )
        game.set_game_master_info(
            GameMasterInfoConfig.from_json(
                {
                    "profile_name": created_by.get_profile_name(),
                    "email_id": created_by.platform_user.get_email(),
                    "phone": created_by.platform_user.get_phone(),
                }
            )
        )
        game.save()

        return game


class Team(AbstractTimeStamped):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="teams")
    team_name = models.CharField(max_length=Length.TEAM_NAME)
    team_colour = models.CharField(max_length=Length.TEAM_COLOUR)

    class Meta:
        indexes = [models.Index(fields=["team_name"]), models.Index(fields=["game", "team_name"])]
        unique_together = (("game", "team_name"),)

    @classmethod
    def create(cls, game: Game, team_name: str, team_colour: str) -> "Team":
        team = cls(game=game, team_name=team_name, team_colour=team_colour)
        team.save()
        return team


class TeamPlayerRelation(AbstractTimeStamped):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)

    game = models.ForeignKey(Game, on_delete=models.CASCADE)  # Denormalized for managing constraint

    class Meta:
        indexes = [models.Index(fields=["team"]), models.Index(fields=["game"])]
        unique_together = (("player", "game"),)

    @classmethod
    def create(cls, team: Team, player: PlayerProfile) -> "TeamPlayerRelation":
        team_player_relation = cls(team=team, player=player, game=team.game)
        team_player_relation.save()
        return team_player_relation
