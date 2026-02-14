from dataclasses import dataclass

from common.popo import PopoBase


@dataclass(init=True, repr=False, eq=False)
class GeoCountConfig(PopoBase):
    count: int

    @classmethod
    def from_json(cls, config: dict) -> "GeoCountConfig":
        if not config:
            return cls.default()

        return cls(count=config.get("count", 1))

    def to_json(self) -> dict:
        return {"count": self.count}

    @classmethod
    def default(cls) -> "GeoCountConfig":
        return cls(count=1)
