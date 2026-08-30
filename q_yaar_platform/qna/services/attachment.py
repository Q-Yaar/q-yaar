"""
Service layer for answer attachments.

Sits between the API layer and the object-storage driver (common.storage).
The API layer (views, serializers) talks to this module, never to the
storage driver directly.

Object keys are namespaced per game so a game's files can be exported by
listing a single prefix:

    games/{game_external_id}/answers/{asked_question_external_id}/{file_id}
"""

import logging

from django.db import transaction

from common.constants import AttachmentStatus
from common.storage import (
    build_object_key,
    object_exists,
    presign_get_url,
    presign_put_url,
)
from common.uuid import unique_uuid4
from profile_player.models import PlayerProfile
from qna.models import AskedQuestion, Attachment

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


def svc_attachment_run_validations_to_request_upload(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("file_name"):
        return ErrorCode(ErrorCode.MISSING_FILE_NAME)

    return None


def svc_attachment_request_upload(asked_question: AskedQuestion, player: PlayerProfile, request_data: dict) -> dict:
    logger.debug(f">> ARGS: {locals()}")

    file_name = request_data["file_name"]
    content_type = request_data.get("content_type", "")

    # The attachment's external_id doubles as the file id, so a key traces
    # back to exactly one row.
    file_id = unique_uuid4()
    game = asked_question.game_question.game
    object_key = build_object_key(
        "games",
        str(game.get_external_id()),
        Attachment.SCOPE_ANSWERS,
        str(asked_question.get_external_id()),
        str(file_id),
    )

    attachment = Attachment(
        asked_question=asked_question,
        uploaded_by=player,
        object_key=object_key,
        file_name=file_name,
        content_type=content_type,
        status=AttachmentStatus.PENDING.value,
    )
    attachment.external_id = file_id
    attachment.save()

    return {
        "attachment_id": str(attachment.external_id),
        "upload_url": presign_put_url(object_key),
        "object_key": object_key,
        "file_name": file_name,
        "content_type": content_type,
    }


def svc_attachment_commit(asked_question: AskedQuestion, attachment_ids: list[str]):
    """Verify ownership + object presence, then mark attachments UPLOADED."""
    logger.debug(f">> ARGS: {locals()}")

    requested_ids = [str(attachment_id) for attachment_id in attachment_ids]

    attachments = list(Attachment.objects.filter(external_id__in=requested_ids, asked_question=asked_question))

    found_ids = {str(a.external_id) for a in attachments}
    missing_ids = set(requested_ids) - found_ids
    if missing_ids:
        return ErrorCode(ErrorCode.INVALID_ATTACHMENT_ID, attachment_id=list(missing_ids)), None

    for a in attachments:
        if a.status == AttachmentStatus.UPLOADED.value:
            return ErrorCode(ErrorCode.ATTACHMENT_ALREADY_COMMITTED, attachment_id=str(a.external_id)), None

    # Confirm the client actually uploaded each object before committing.
    for a in attachments:
        if not object_exists(a.object_key):
            return ErrorCode(ErrorCode.ATTACHMENT_NOT_UPLOADED, attachment_id=str(a.external_id)), None

    with transaction.atomic():
        Attachment.objects.filter(pk__in=[a.pk for a in attachments]).update(status=AttachmentStatus.UPLOADED.value)

    return None, attachments


def svc_attachment_serialize_for_asked_question(
    asked_question: AskedQuestion,
) -> list[dict]:
    """Return uploaded attachments for a question as plain dicts with presigned GET URLs."""
    attachments = asked_question.attachments.filter(status=AttachmentStatus.UPLOADED.value).order_by("created")

    return [
        {
            "attachment_id": str(a.get_external_id()),
            "file_name": a.file_name,
            "content_type": a.content_type,
            "url": presign_get_url(a.object_key),
            "created": a.created,
        }
        for a in attachments
    ]
