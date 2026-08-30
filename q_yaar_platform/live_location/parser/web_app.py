from live_location.parser.base import AbstractLocationParser
from live_location.parser.response_format import LocationResponseFormat


class WebAppParser(AbstractLocationParser):
    def parse(self, data: dict) -> LocationResponseFormat:
        return LocationResponseFormat(
            lat=float(data.get("latitude")),
            lon=float(data.get("longitude")),
            raw_data=data,
            accuracy=float(data.get("accuracy", 0.0)),
        )
