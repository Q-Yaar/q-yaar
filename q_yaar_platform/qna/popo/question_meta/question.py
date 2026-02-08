from dataclasses import dataclass

from common.popo import PopoBase


@dataclass(init=True, repr=False, eq=False)
class LocationPointConfig(PopoBase):
    lat: str
    lon: str

    @classmethod
    def from_json(cls, config: dict) -> "LocationPointConfig":
        if not config:
            return cls.default()
        return cls(lat=config["lat"], lon=config["lon"])

    def to_json(self) -> dict:
        return {"lat": self.lat, "lon": self.lon}


@dataclass(init=True, repr=False, eq=False)
class LocationPointListConfig(PopoBase):
    location_points: list[LocationPointConfig]

    @classmethod
    def from_json(cls, config: list[dict]) -> "LocationPointListConfig":
        if not config:
            return cls.default()
        return cls(location_points=[LocationPointConfig.from_json(point) for point in config])

    def to_json(self) -> list[dict]:
        return [point.to_json() for point in self.location_points]


@dataclass(init=True, repr=False, eq=False)
class QuestionMetaConfig(PopoBase):
    # Just a wrapper class, actual classes defined in reward_types_map.py
    location_points: LocationPointListConfig

    @classmethod
    def from_json(cls, config: dict) -> "QuestionMetaConfig":
        if not config:
            return cls.default()
        return cls(location_points=LocationPointListConfig.from_json(config["location_points"]))

    def to_json(self) -> dict:
        return {"location_points": self.location_points.to_json()}
