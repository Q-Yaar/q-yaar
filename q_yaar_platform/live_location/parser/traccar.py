from live_location.parser.base import AbstractLocationParser
from live_location.parser.response_format import LocationResponseFormat


class TraccarParser(AbstractLocationParser):
    def parse(self, data: dict) -> LocationResponseFormat:
        lat = data["location"]["coords"]["latitude"]
        lon = data["location"]["coords"]["longitude"]
        accuracy = data["location"]["coords"]["accuracy"]

        return LocationResponseFormat(lat=lat, lon=lon, raw_data=data, accuracy=accuracy)
