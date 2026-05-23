from common.abstract_models import AbstractExternalFacing, AbstractLocationPoint, AbstractTimeStamped
from common.constants import LocationClientType
from django.contrib.gis.geos import Point
from django.db import models
from profile_player.models import PlayerProfile


class LocationSharingSetting(AbstractExternalFacing, AbstractTimeStamped):
    player = models.OneToOneField(
        PlayerProfile, on_delete=models.CASCADE, related_name="location_sharing_setting", unique=True
    )
    is_sharing_enabled = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["player"])]

    def __str__(self):
        return f"{self.player} - Sharing: {self.is_sharing_enabled}"

    @classmethod
    def create(cls, player: PlayerProfile) -> "LocationSharingSetting":
        setting = cls(player=player)
        setting.save()
        return setting


class LiveLocation(AbstractLocationPoint, AbstractTimeStamped):
    CONST_KEY_TRACKING_META = "tracking_meta"

    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)

    accuracy = models.FloatField(null=True, blank=True)
    client = models.PositiveIntegerField(choices=LocationClientType.get_choices())

    info = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=["player", "-created"])]

    def get_tracking_meta(self):
        return self.info.get(self.CONST_KEY_TRACKING_META, {})

    def set_tracking_meta(self, tracking_meta: dict, save: bool = False):
        info = self.info
        info[self.CONST_KEY_TRACKING_META] = tracking_meta
        self.info = info
        if save:
            self.save()
        return self

    @classmethod
    def create(
        cls,
        player: PlayerProfile,
        location_pnt: Point,
        accuracy: float,
        client: LocationClientType,
        tracking_meta: dict,
    ) -> "LiveLocation":
        live_location = cls(player=player, location_pnt=location_pnt, accuracy=accuracy, client=client)
        live_location.set_tracking_meta(tracking_meta)
        live_location.save()
        return live_location
