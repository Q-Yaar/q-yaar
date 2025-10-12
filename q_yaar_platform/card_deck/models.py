import pghistory
from common.abstract_models import AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import JSONField


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
    def create(cls, title: str, description: str, image: str, reward: int = None, metadata: dict = {}) -> "Card":
        card = cls(title=title, description=description, image=image, reward=reward, metadata=metadata)
        card.save()
        return card
