import pghistory
from common.abstract_models import AbstractExternalFacing, AbstractTimeStamped
from common.constants import ClientType, Length
from django.db import models
from game.models import Game, Team
from profile_player.models import PlayerProfile


@pghistory.track()
class Location(AbstractExternalFacing, AbstractTimeStamped):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="locations")
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True, related_name="locations")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="locations")

    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy = models.FloatField(null=True, blank=True)
    reported_time = models.DateTimeField()

    client = models.PositiveIntegerField(choices=ClientType.get_choices())

    class Meta:
        indexes = [
            models.Index(fields=["player"]),
            models.Index(fields=["game"]),
            models.Index(fields=["team"]),
        ]

    def __str__(self):
        return f"{self.player} at {self.lat},{self.lon}"

    @classmethod
    def create(
        cls,
        player: PlayerProfile,
        lat: float,
        lon: float,
        reported_time,
        client: ClientType,
        game: Game = None,
        team: Team = None,
        accuracy: float = None,
    ) -> "Location":
        location = cls(
            player=player,
            game=game,
            team=team,
            lat=lat,
            lon=lon,
            accuracy=accuracy,
            reported_time=reported_time,
            client=client.value if isinstance(client, ClientType) else ClientType.tokentype_from_string(client).value,
        )
        location.save()
        return location


class LocationSharingSetting(AbstractTimeStamped):
    player = models.OneToOneField(PlayerProfile, on_delete=models.CASCADE, related_name="location_sharing_setting")
    is_sharing_enabled = models.BooleanField(default=False)
    tracking_code = models.CharField(max_length=Length.TRACKING_CODE, blank=True, null=True, unique=True)

    class Meta:
        indexes = [models.Index(fields=["tracking_code"])]

    def __str__(self):
        return f"{self.player} - Sharing: {self.is_sharing_enabled}"

    @classmethod
    def create(cls, player: PlayerProfile) -> "LocationSharingSetting":
        setting = cls(player=player)
        setting.save()
        return setting
