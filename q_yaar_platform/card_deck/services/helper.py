import logging

from card_deck.models import Card
from card_deck.services.error_codes import ErrorCode
from django.db import transaction

logger = logging.getLogger(__name__)


def svc_card_deck_helper_validate_and_get_request_data(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("tag_name"):
        return ErrorCode(ErrorCode.MISSING_TAG_NAME), None

    return None, request_data


def svc_card_deck_helper_get_cards_by_tag(tag_name: str):
    logger.debug(f">> ARGS: {locals()}")

    return Card.objects.filter(tags__icontains=tag_name)


def svc_card_deck_helper_validate_input_for_bulk_create(cards_data: list[dict]):
    logger.debug(f">> ARGS: {locals()}")

    required_fields = {"title", "description"}
    allowed_fields = {
        "title": str,
        "description": str,
        "image": str,
        "reward": int,
        "tags": list,
        "metadata": dict,
    }

    for idx, card_data in enumerate(cards_data):
        missing_fields = required_fields - card_data.keys()
        if missing_fields:
            return ErrorCode(ErrorCode.MISSING_MANDATORY_FIELD, index=idx, missing_fields=missing_fields), None

        for field in required_fields:
            if not isinstance(card_data[field], allowed_fields[field]):
                return (
                    ErrorCode(
                        ErrorCode.INVALID_FIELD_TYPE, index=idx, field_name=field, expected_type=allowed_fields[field]
                    ),
                    None,
                )

        for field, value in card_data.items():
            if field not in allowed_fields:
                return ErrorCode(ErrorCode.INVALID_FIELD_NAME, index=idx, field_name=field), None
            if value and not isinstance(value, allowed_fields[field]):
                return (
                    ErrorCode(
                        ErrorCode.INVALID_FIELD_TYPE, index=idx, field_name=field, expected_type=allowed_fields[field]
                    ),
                    None,
                )

    return None, cards_data


def svc_card_deck_helper_bulk_create_cards(cards_data: list[dict]):
    logger.debug(f">> ARGS: {locals()}")

    with transaction.atomic():
        cards = [Card.create(**card_data) for card_data in cards_data]

    return cards
