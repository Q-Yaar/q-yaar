from django.db import models

from account.models import PlatformUser
from common.abstract_models import AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned
from common.constants import AssetStatus, Length


class Asset(AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned):
    # Object keys are namespaced per bucket:
    #   {bucket}/{file_id}
    # `file_id` is a uuid4 separate from this row's external_id.
    # The asset has no direct link to any game or other context —
    # association is handled by relation tables in the consuming app.

    uploaded_by = models.ForeignKey(
        PlatformUser,
        on_delete=models.CASCADE,
        related_name="media_assets",
    )

    object_key = models.CharField(max_length=Length.ASSET_OBJECT_KEY)
    asset_name = models.CharField(max_length=Length.ASSET_NAME)
    content_type = models.CharField(max_length=Length.ASSET_CONTENT_TYPE, blank=True, default="")

    status = models.PositiveIntegerField(choices=AssetStatus.get_choices(), default=AssetStatus.PENDING.value)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.object_key

    @classmethod
    def create(
        cls,
        *,
        external_id,
        uploaded_by,
        object_key: str,
        asset_name: str,
        content_type: str = "",
    ) -> "Asset":
        asset = cls(
            external_id=external_id,
            uploaded_by=uploaded_by,
            object_key=object_key,
            asset_name=asset_name,
            content_type=content_type,
            status=AssetStatus.PENDING.value,
        )
        asset.save()
        return asset


class AssetAskedQuestionRelation(AbstractTimeStamped):
    # Links an asset to the asked question it serves as evidence for.
    # Exclusive binding: one asset belongs to at most one asked question,
    # enforced by unique=True on the asset field. New attachment targets get
    # their own relation class instead of overloading Asset.

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="asked_question_links", unique=True)
    asked_question = models.ForeignKey("qna.AskedQuestion", on_delete=models.CASCADE, related_name="asset_links")

    class Meta:
        indexes = [models.Index(fields=["asked_question"])]

    @classmethod
    def create(cls, *, asset: Asset, asked_question) -> "AssetAskedQuestionRelation":
        relation = cls(asset=asset, asked_question=asked_question)
        relation.save()
        return relation
