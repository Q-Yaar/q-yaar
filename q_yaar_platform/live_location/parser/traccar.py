from live_location.parser.base import AbstractLocationParser
from live_location.parser.response_format import LocationResponseFormat


class TraccarParser(AbstractLocationParser):
    def parse(self, data) -> LocationResponseFormat:
        if "lat" in data and "lon" in data:
            lat = float(data.get("lat"))
            lon = float(data.get("lon"))
            
            accuracy_val = data.get("accuracy")
            accuracy = 0.0
            if accuracy_val:
                try:
                    accuracy = float(accuracy_val)
                except ValueError:
                    pass
            return LocationResponseFormat(lat=lat, lon=lon, raw_data=data, accuracy=accuracy)
            
        elif "location" in data and "coords" in data["location"]:
            coords = data["location"]["coords"]
            lat = float(coords["latitude"])
            lon = float(coords["longitude"])
            
            accuracy_val = coords.get("accuracy")
            accuracy = 0.0
            if accuracy_val:
                try:
                    accuracy = float(accuracy_val)
                except ValueError:
                    pass
            return LocationResponseFormat(lat=lat, lon=lon, raw_data=data, accuracy=accuracy)
            
        else:
            raise KeyError("Unable to parse location data: missing latitude/longitude")
