import logging

from card_deck.models import Card, CardTag
from card_deck.services.error_codes import ErrorCode
from django.db import IntegrityError, transaction

logger = logging.getLogger(__name__)


def svc_card_deck_helper_validate_and_get_request_data(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("tag_name"):
        return ErrorCode(ErrorCode.MISSING_TAG_NAME), None

    return None, request_data


def svc_card_deck_helper_get_cards_by_tag(tag_name: str):
    logger.debug(f">> ARGS: {locals()}")

    return Card.objects.filter(tags__icontains=tag_name).order_by("-created")


def svc_card_deck_helper_validate_input_for_bulk_create(cards_data: list[dict]):
    logger.debug(f">> ARGS: {locals()}")

    required_fields = {"title", "description", "tags"}
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
            return ErrorCode(ErrorCode.MISSING_MANDATORY_FIELD, index=idx, missing_fields=missing_fields)

        for field in required_fields:
            if not isinstance(card_data[field], allowed_fields[field]):
                return ErrorCode(
                    ErrorCode.INVALID_FIELD_TYPE, index=idx, field_name=field, expected_type=allowed_fields[field]
                )
            if not card_data[field]:
                return ErrorCode(ErrorCode.EMPTY_MANDATORY_FIELD, index=idx, field_name=field)

        for field, value in card_data.items():
            if field not in allowed_fields:
                return ErrorCode(ErrorCode.INVALID_FIELD_NAME, index=idx, field_name=field)
            if value and not isinstance(value, allowed_fields[field]):
                return ErrorCode(
                    ErrorCode.INVALID_FIELD_TYPE, index=idx, field_name=field, expected_type=allowed_fields[field]
                )

        tags = card_data.get("tags")
        extracted_tags = CardTag.objects.filter(name__in=tags).values_list("name", flat=True)
        missing_tags = set(tags) - set(extracted_tags)
        if missing_tags:
            return ErrorCode(ErrorCode.INVALID_TAG_NAMES, invalid_tags=list(missing_tags))

    return None


def svc_card_deck_helper_validate_input_for_tag_creation(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("tag_name"):
        return ErrorCode(ErrorCode.MISSING_TAG_NAME)

    return None


def svc_card_deck_helper_get_tags_from_card_data(card_data: dict) -> list[str]:
    logger.debug(f">> ARGS: {locals()}")

    return CardTag.objects.filter(name__in=card_data["tags"])


def svc_card_deck_helper_bulk_create_cards(cards_data: list[dict]):
    logger.debug(f">> ARGS: {locals()}")

    for card_data in cards_data:
        card_data["tags"] = svc_card_deck_helper_get_tags_from_card_data(card_data=card_data)

    with transaction.atomic():
        cards = [Card.create(**card_data) for card_data in cards_data]

    return cards


def svc_card_deck_helper_get_list_of_tags() -> list[str]:
    logger.debug(f">> ARGS: {locals()}")

    return list(CardTag.objects.all().values_list("name", flat=True))


def svc_card_deck_helper_create_tag(tag_name: str) -> tuple[None | ErrorCode, CardTag | None]:
    logger.debug(f">> ARGS: {locals()}")

    try:
        tag = CardTag.create(name=tag_name)
        return None, tag
    except IntegrityError:
        return ErrorCode(ErrorCode.TAG_ALREADY_EXISTS, tag_name=tag_name), None
