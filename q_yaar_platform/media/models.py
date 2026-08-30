from django.conf import settings
from django.db import models

from common.abstract_models import AbstractExternalFacing, AbstractTimeStamped
from common.constants import AssetStatus, Length, UserRolesType
from game.models import Game


class Asset(AbstractExternalFacing, AbstractTimeStamped):
    # Object keys are namespaced per game so a game's files can be
    # listed/exported by a single prefix:
    #   games/{game_external_id}/{role}/{user_external_id}/{file_id}
    # `file_id` == this row's external_id, so a key traces back to one row.

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="media_assets",
    )
    role = models.PositiveIntegerField(choices=UserRolesType.get_choices())
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="media_assets")

    # When non-null, this asset is attached as evidence to a specific answer.
    # Exclusive binding: one asset belongs to at most one asked question.
    asked_question = models.ForeignKey(
        "qna.AskedQuestion",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attachments",
    )

    object_key = models.CharField(max_length=Length.ASSET_OBJECT_KEY)
    asset_name = models.CharField(max_length=Length.ASSET_NAME)
    content_type = models.CharField(max_length=Length.ASSET_CONTENT_TYPE, blank=True, default="")

    status = models.PositiveIntegerField(choices=AssetStatus.get_choices(), default=AssetStatus.PENDING.value)

    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=["game"]),
            models.Index(fields=["status"]),
            models.Index(fields=["asked_question"]),
        ]

    def __str__(self):
        return self.object_key

    @classmethod
    def create(
        cls,
        *,
        external_id,
        uploaded_by,
        role: UserRolesType,
        game: Game,
        object_key: str,
        asset_name: str,
        content_type: str = "",
    ) -> "Asset":
        asset = cls(
            external_id=external_id,
            uploaded_by=uploaded_by,
            role=role.value,
            game=game,
            object_key=object_key,
            asset_name=asset_name,
            content_type=content_type,
            status=AssetStatus.PENDING.value,
        )
        asset.save()
        return asset
