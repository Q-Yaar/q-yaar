from dataclasses import dataclass


@dataclass
class LocationResponseFormat:
    lat: float
    lon: float
    raw_data: dict
    accuracy: float = 0.0
