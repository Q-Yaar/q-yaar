from common.abstract_models import AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned
from common.constants import GameStatus, GameType, Length
from django.db import models

from common.uuid import unique_uuid4
from game.popo.game_master_info import GameMasterInfoConfig
from game.popo.teams_info import TeamInfoListConfig
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
    players = models.ManyToManyField(PlayerProfile, related_name="games", blank=True)

    info = models.JSONField(default=dict, blank=True)

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

    def get_teams_info(self) -> TeamInfoListConfig:
        return TeamInfoListConfig.from_json(self.info.get(self.CONST_KEY_TEAMS_INFO))

    def set_teams_info(self, config: TeamInfoListConfig, save: bool = False) -> None:
        info = self.info
        info[self.CONST_KEY_TEAMS_INFO] = config.to_json()
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
        players: list[PlayerProfile],
        teams_info: TeamInfoListConfig,
    ) -> "Game":
        game_code = str(unique_uuid4())[:6]
        game = cls(
            game_type=game_type.value, game_code=game_code, name=name, description=description, created_by=created_by
        )
        game.save()

        game.players.add(*players)
        game.set_game_master_info(
            GameMasterInfoConfig.from_json(
                {
                    "profile_name": created_by.get_profile_name(),
                    "email_id": created_by.platform_user.get_email(),
                    "phone": created_by.platform_user.get_phone(),
                }
            )
        )
        game.set_teams_info(teams_info)
        game.save()

        return game
