import logging

from card_deck.models import Card
from card_deck.services.error_codes import ErrorCode

logger = logging.getLogger(__name__)


def svc_card_deck_helper_validate_and_get_request_data(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("tag_name"):
        return ErrorCode(ErrorCode.MISSING_TAG_NAME), None

    return None, request_data


def svc_card_deck_helper_get_cards_by_tag(tag_name: str):
    logger.debug(f">> ARGS: {locals()}")

    return Card.objects.filter(tags__icontains=tag_name)
