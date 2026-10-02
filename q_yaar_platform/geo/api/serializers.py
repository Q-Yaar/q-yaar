from rest_framework import serializers

from geo.models import GeoFeature


class GeoFeatureSerializer(serializers.ModelSerializer):
    """Compact representation for feature lists: {lat, lng} location"""

    fclass = serializers.CharField(source="feature_class", read_only=True)
    location = serializers.SerializerMethodField()

    class Meta:
        model = GeoFeature
        fields = ("id", "osm_id", "name", "source", "fclass", "tags", "location")

    def get_location(self, obj: GeoFeature) -> dict:
        return obj.get_location_dict()


class GeoFeatureDetailSerializer(GeoFeatureSerializer):
    """Detail representation: adds the boundary as GeoJSON"""

    geometry = serializers.SerializerMethodField()

    class Meta(GeoFeatureSerializer.Meta):
        fields = GeoFeatureSerializer.Meta.fields + ("geometry",)

    def get_geometry(self, obj: GeoFeature) -> dict:
        return obj.get_geojson()
