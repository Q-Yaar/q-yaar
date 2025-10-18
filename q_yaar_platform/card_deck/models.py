import pghistory
from common.abstract_models import AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned
from common.constants import CardPile
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import JSONField
from profile_player.models import PlayerProfile


@pghistory.track()
class Card(AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField(max_length=200, blank=True, null=True)

    reward = models.PositiveIntegerField(default=None, blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)

    metadata = JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["title"]), models.Index(fields=["tags"])]

    @classmethod
    def create(
        cls, title: str, description: str, image: str, reward: int = None, tags: list[str] = [], metadata: dict = {}
    ) -> "Card":
        card = cls(title=title, description=description, image=image, reward=reward, tags=tags, metadata=metadata)
        card.save()
        return card


# class CardDeck(AbstractTimeStamped):
#     players = models.ManyToManyField(PlayerProfile, related_name="player_deck")
#     cards = models.ManyToManyField(Card, related_name="decks")


# class CardInstance(AbstractTimeStamped):
#     card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="instances")
#     deck = models.ForeignKey(CardDeck, on_delete=models.CASCADE, related_name="card_instances")

#     pile = models.PositiveSmallIntegerField(choices=CardPile.get_choices(), default=CardPile.DECK.value)

#     class Meta:
        # indexes = [models.Index(fields=["pile"]), models.Index(fields=["deck", "pile"])]
