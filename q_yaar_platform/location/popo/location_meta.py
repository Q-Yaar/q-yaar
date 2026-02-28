import dataclasses
from common.constants import LocationClientType


@dataclasses.dataclass
class LocationPointData:
    lat: float
    lon: float
    timestamp: str
    accuracy: float = None


@dataclasses.dataclass
class LocationAddData:
    game_id: str
    team_id: str
    client: LocationClientType
    locations: list[LocationPointData]
