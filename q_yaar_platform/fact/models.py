from common.abstract_models import AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned
from common.constants import FactType
from django.db import models
from game.models import Game, Team


class Fact(AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned):
    # TODO: Add POPOs in future, currently fully flexible.
    CONST_KEY_FACT_INFO = "fact_info"

    fact_type = models.PositiveIntegerField(choices=FactType.get_choices())
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="facts")
    target_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="facts")

    info = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["fact_type"]),
            models.Index(fields=["game"]),
            models.Index(fields=["target_team"]),
            models.Index(fields=["game", "target_team"]),
        ]

    def __str__(self):
        return f"{self.get_external_id()}"

    def get_fact_info(self) -> dict:
        return self.info.get(self.CONST_KEY_FACT_INFO, {})

    def set_fact_info(self, fact_info: dict, save: bool = False) -> "Fact":
        info = self.info
        info[self.CONST_KEY_FACT_INFO] = fact_info
        self.info = info
        if save:
            self.save()

        return self

    @classmethod
    def create(cls, fact_type: FactType, game: Game, target_team: Team, fact_info: dict) -> "Fact":
        fact = cls(fact_type=fact_type, game=game, target_team=target_team, info=fact_info)
        fact.save()
        return fact
