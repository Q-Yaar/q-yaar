import logging

from card_deck.api.serializers import CardSerializer
from card_deck.services.error_codes import ErrorCode
from card_deck.services.helper import (
    svc_card_deck_helper_bulk_create_cards,
    svc_card_deck_helper_create_tag,
    svc_card_deck_helper_get_cards_by_tag,
    svc_card_deck_helper_get_list_of_tags,
    svc_card_deck_helper_validate_and_get_request_data,
    svc_card_deck_helper_validate_input_for_bulk_create,
    svc_card_deck_helper_validate_input_for_tag_creation,
)

logger = logging.getLogger(__name__)


def svc_card_deck_get_cards_by_tag(request_data: dict, serialized: bool = False):
    logger.debug(f">> ARGS: {locals()}")

    error, request_data = svc_card_deck_helper_validate_and_get_request_data(request_data=request_data)
    if error:
        return error, None

    cards = svc_card_deck_helper_get_cards_by_tag(tag_name=request_data["tag_name"])

    if serialized:
        cards = CardSerializer(cards, many=True).data

    return ErrorCode(ErrorCode.SUCCESS), cards


def svc_card_deck_bulk_create_cards(request_data: list[dict]):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_card_deck_helper_validate_input_for_bulk_create(cards_data=request_data)
    if error:
        return error, None

    cards = svc_card_deck_helper_bulk_create_cards(cards_data=request_data)

    return ErrorCode(ErrorCode.SUCCESS), cards


def svc_card_deck_get_list_of_tags(serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    tags = svc_card_deck_helper_get_list_of_tags()

    if serialized:
        tags = {"tags": tags}

    return ErrorCode(ErrorCode.SUCCESS), tags


def svc_card_deck_create_tag(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_card_deck_helper_validate_input_for_tag_creation(request_data=request_data)
    if error:
        return error, None

    error, tag = svc_card_deck_helper_create_tag(tag_name=request_data["tag_name"])
    if error:
        return error, None
    return ErrorCode(ErrorCode.CREATED), {"tag": tag.name}
