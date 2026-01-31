from dataclasses import dataclass

from qna.popo.reward_meta.reward import RewardConfig


@dataclass(init=True, repr=False, eq=False)
class CardDrawRewardConfig(RewardConfig):
    draw: int
    pick: int

    @classmethod
    def from_json(cls, config: dict) -> "CardDrawRewardConfig":
        return cls(draw=config["draw"], pick=config["pick"])

    def to_json(self) -> dict:
        return {"draw": self.draw, "pick": self.pick}
