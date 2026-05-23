from common.constants import LocationClientType
from live_location.parser.base import AbstractLocationParser
from live_location.parser.response_format import LocationResponseFormat
from live_location.parser.traccar import TraccarParser


class LocationParserClient(AbstractLocationParser):
    client_type: LocationClientType

    def __init__(self, client_type: LocationClientType):
        self.client_type = client_type

    def parse(self, data: dict) -> LocationResponseFormat:
        LOCATION_CLIENT_MAP = {
            LocationClientType.TRACCAR: TraccarParser,
        }

        client = LOCATION_CLIENT_MAP[self.client_type]()
        return client.parse(data)
