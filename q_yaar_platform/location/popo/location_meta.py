import dataclasses
from common.constants import ClientType


@dataclasses.dataclass
class LocationPointData:
    lat: float
    lon: float
    reported_time: str
    accuracy: float = None


@dataclasses.dataclass
class LocationAddData:
    game_id: str
    team_id: str
    client: ClientType
    locations: list[LocationPointData]
