from fact.models import Fact
from common.constants import FactType
from rest_framework import serializers


class FactSerializer(serializers.ModelSerializer):
    fact_id = serializers.SerializerMethodField()
    fact_type = serializers.SerializerMethodField()
    fact_info = serializers.SerializerMethodField()

    class Meta:
        model = Fact
        fields = ("fact_id", "fact_type", "fact_info", "created", "modified")

    def get_fact_id(self, obj: Fact) -> str:
        return str(obj.get_external_id())

    def get_fact_type(self, obj: Fact) -> str:
        return FactType.get_string_for_type(FactType(obj.fact_type))

    def get_fact_info(self, obj: Fact) -> dict:
        return obj.get_fact_info()
