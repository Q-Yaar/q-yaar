from abc import ABC, abstractmethod

from live_location.parser.response_format import LocationResponseFormat


class AbstractLocationParser(ABC):
    @abstractmethod
    def parse(self, data: dict) -> LocationResponseFormat:
        pass
