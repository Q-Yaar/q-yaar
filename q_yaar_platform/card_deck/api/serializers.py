from card_deck.models import Card
from rest_framework import serializers


class CardSerializer(serializers.ModelSerializer):
    card_id = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = ("card_id", "title", "description", "image", "reward", "tags", "metadata", "created", "modified")

    def get_card_id(self, obj: Card) -> str:
        return str(obj.get_external_id())
