import pghistory

from django.db import models

from common.abstract_models import AbstractTimeStamped, AbstractUserProfile, AbstractVersioned


@pghistory.track()
class GameMasterProfile(AbstractUserProfile, AbstractTimeStamped, AbstractVersioned):
    def __str__(self) -> str:
        return f"{self.profile_name} - {self.platform_user}"

    class Meta:
        indexes = [models.Index(fields=["platform_user"])]

    @classmethod
    def create(cls, platform_user, profile_name: str, profile_pic: dict = {}) -> "GameMasterProfile":
        if not profile_pic:
            profile_pic = {}
        game_master = cls(platform_user=platform_user, profile_name=profile_name, profile_pic=profile_pic)
        game_master.save()
        return game_master
