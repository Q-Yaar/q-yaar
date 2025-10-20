import pghistory
from common.abstract_models import AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned
from common.constants import CardPile, Length
from django.db import models
from django.db.models import JSONField
from game.models import Game, Team
from profile_player.models import PlayerProfile


class CardTag(AbstractTimeStamped, AbstractVersioned):
    name = models.CharField(max_length=Length.CARD_TAG, unique=True)

    class Meta:
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, name: str) -> "CardTag":
        tag = cls(name=name)
        tag.save()
        return tag


@pghistory.track()
class Card(AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned):
    title = models.CharField(max_length=Length.CARD_TITLE)
    description = models.TextField()
    image = models.URLField(max_length=Length.CARD_IMAGE_URL, blank=True, null=True)

    reward = models.PositiveIntegerField(default=None, blank=True, null=True)
    tags = models.ManyToManyField(CardTag, related_name="cards", blank=True)

    metadata = JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["title"])]

    def __str__(self):
        return self.title

    @classmethod
    def create(
        cls, title: str, description: str, image: str, tags: list[CardTag], reward: int = None, metadata: dict = {}
    ) -> "Card":
        card = cls(title=title, description=description, image=image, reward=reward, metadata=metadata)
        card.save()
        card.tags.add(*tags)
        card.save()
        return card


# List of this forms a deck of cards
class CardInstance(AbstractTimeStamped):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="instances")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="cards")

    pile = models.PositiveSmallIntegerField(choices=CardPile.get_choices(), default=CardPile.DECK.value)

    class Meta:
        indexes = [models.Index(fields=["team", "pile"])]

    @classmethod
    def create(cls, card: Card, team: Team) -> "CardInstance":
        card_instance = cls(card=card, team=team)
        card_instance.save()
        return card_instance
