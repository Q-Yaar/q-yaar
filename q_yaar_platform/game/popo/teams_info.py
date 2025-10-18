from dataclasses import dataclass

from common.popo import PopoBase


@dataclass(init=True, repr=False, eq=False)
class TeamInfoConfig(PopoBase):
    team_name: str
    team_color: str
    members: list[str]

    @classmethod
    def from_json(cls, config: dict) -> "TeamInfoConfig":
        return cls(
            team_name=config.get("team_name", ""),
            team_color=config.get("team_color", ""),
            members=config.get("members", []),
        )

    def to_json(self) -> dict:
        return {"team_name": self.team_name, "team_color": self.team_color, "members": self.members}


@dataclass(init=True, repr=False, eq=False)
class TeamInfoListConfig(PopoBase):
    teams: list[TeamInfoConfig]

    @classmethod
    def from_json(cls, config: list[dict]) -> "TeamInfoListConfig":
        return cls(teams=[TeamInfoConfig.from_json(team_config) for team_config in config])

    def to_json(self) -> list[dict]:
        return [team.to_json() for team in self.teams]
