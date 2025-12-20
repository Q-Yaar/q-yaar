from card_deck.models import Card
from common.constants import CardType
from rest_framework import serializers


class CardSerializer(serializers.ModelSerializer):
    card_id = serializers.SerializerMethodField()
    card_type = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = (
            "card_id",
            "title",
            "description",
            "card_type",
            "image",
            "tags",
            "reward",
            "metadata",
            "created",
            "modified",
        )

    def get_card_id(self, obj: Card) -> str:
        return str(obj.get_external_id())

    def get_card_type(self, obj: Card) -> str:
        return CardType.get_string_for_type(CardType(obj.card_type))

    def get_tags(self, obj: Card) -> list[str]:
        return [tag.name for tag in obj.tags.all()]
