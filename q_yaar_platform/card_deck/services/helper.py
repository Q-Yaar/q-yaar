import logging
import uuid

from card_deck.models import Card, CardInstance, CardTag
from card_deck.services.error_codes import ErrorCode
from django.db import IntegrityError, transaction
from common.constants import CardPile
from game.models import Team
from game.services.interfacer import svc_game_get_team_by_id, svc_game_verify_player_belongs_to_team
from profile_player.models import PlayerProfile

logger = logging.getLogger(__name__)


def svc_card_deck_helper_validate_and_get_request_data(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("tag_name"):
        return ErrorCode(ErrorCode.MISSING_TAG_NAME), None

    return None, request_data


def svc_card_deck_helper_get_cards_by_tag(tag_name: str):
    logger.debug(f">> ARGS: {locals()}")

    return Card.objects.filter(tags__name__icontains=tag_name).order_by("-created")


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


def svc_card_deck_helper_validate_input_for_team_deck_creation(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("card_ids"):
        return ErrorCode(ErrorCode.MISSING_CARD_IDS)

    extracted_ids = Card.objects.filter(external_id__in=request_data["card_ids"]).values_list("external_id", flat=True)
    missing_ids = set(str(card_id) for card_id in request_data["card_ids"]) - set(
        str(card_id) for card_id in extracted_ids
    )
    if missing_ids:
        return ErrorCode(ErrorCode.INVALID_CARD_IDS, invalid_card_ids=list(missing_ids))

    return None


def svc_card_deck_helper_validate_input_for_peek(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("num_cards"):
        return ErrorCode(ErrorCode.MISSING_NUM_CARDS)

    return None


def svc_card_deck_helper_validate_input_and_get_piles_for_shuffle(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("piles"):
        return ErrorCode(ErrorCode.MISSING_PILES), None

    piles = request_data["piles"]
    if not isinstance(piles, list):
        return ErrorCode(ErrorCode.INVALID_PILES_FORMAT), None

    pile_names = []
    for pile_name in piles:
        try:
            pile = CardPile.tokentype_from_string(pile_name)
            pile_names.append(pile.value)
        except KeyError:
            return ErrorCode(ErrorCode.INVALID_PILE_NAME, pile_name=pile_name), None

    return None, pile_names


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


def svc_card_deck_helper_get_team_by_id(team_id: uuid.UUID):
    return svc_game_get_team_by_id(team_id=team_id)


def svc_card_deck_helper_create_deck_for_team(team: Team, card_ids: list[uuid.UUID]):
    logger.debug(f">> ARGS: {locals()}")

    # It is allowed to create multiple instances of the same card
    with transaction.atomic():
        for card_id in card_ids:
            card = Card.objects.get(external_id=card_id)
            CardInstance.create(card=card, team=team)

    return None


def svc_card_deck_helper_get_deck_for_team(team: Team):
    logger.debug(f">> ARGS: {locals()}")

    card_ids = CardInstance.objects.filter(team=team).order_by("pile").values_list("card", flat=True)
    cards = []
    for card_id in card_ids:
        cards.append(Card.objects.get(pk=card_id))

    return cards


def svc_card_deck_helper_validate_player_is_in_team(team: Team, player: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_verify_player_belongs_to_team(player=player, team=team)


def svc_card_deck_helper_get_card_stats(team: Team):
    logger.debug(f">> ARGS: {locals()}")

    total_cards = CardInstance.objects.filter(team=team).count()
    deck_cards = CardInstance.objects.filter(team=team, pile=CardPile.DECK.value).count()
    hand_cards = CardInstance.objects.filter(team=team, pile=CardPile.HAND.value).count()
    discard_cards = CardInstance.objects.filter(team=team, pile=CardPile.DISCARD.value).count()

    return {
        "total_cards": total_cards,
        "deck_cards": deck_cards,
        "hand_cards": hand_cards,
        "discard_cards": discard_cards,
    }


def svc_card_deck_helper_peek_cards(team: Team, num_cards: int):
    logger.debug(f">> ARGS: {locals()}")

    card_instances = CardInstance.objects.filter(team=team, pile=CardPile.DECK.value).order_by("?")[:num_cards]

    cards = [instance.card for instance in card_instances]

    return cards


def svc_card_deck_helper_view_hand_pile(team: Team):
    logger.debug(f">> ARGS: {locals()}")

    card_instances = CardInstance.objects.filter(team=team, pile=CardPile.HAND.value)

    cards = [instance.card for instance in card_instances]

    return cards


def svc_card_deck_helper_view_discard_pile(team: Team):
    logger.debug(f">> ARGS: {locals()}")

    card_instances = CardInstance.objects.filter(team=team, pile=CardPile.DISCARD.value)

    cards = [instance.card for instance in card_instances]

    return cards


def svc_card_deck_helper_get_card_instance_by_card_id(card_id: uuid.UUID, team: Team, pile: CardPile):
    logger.debug(f">> ARGS: {locals()}")

    card_instance = CardInstance.objects.filter(card__external_id=card_id, team=team, pile=pile.value).first()
    if not card_instance:
        return (
            ErrorCode(
                ErrorCode.CARD_NOT_AVAILABLE_FOR_ACTION,
                card_id=card_id,
                pile_name=CardPile.get_string_for_type(CardPile(pile)),
            ),
            None,
        )

    return None, card_instance


def svc_card_deck_helper_draw_card(card_instance: CardInstance):
    logger.debug(f">> ARGS: {locals()}")

    card_instance.pile = CardPile.HAND.value
    card_instance.save()

    return card_instance


def svc_card_deck_helper_discard_card(card_instance: CardInstance):
    logger.debug(f">> ARGS: {locals()}")

    card_instance.pile = CardPile.DISCARD.value
    card_instance.save()

    return card_instance


def svc_card_deck_helper_return_card(card_instance: CardInstance):
    logger.debug(f">> ARGS: {locals()}")

    card_instance.pile = CardPile.DECK.value
    card_instance.save()

    return card_instance


def svc_card_deck_helper_shuffle_deck(team: Team, piles: list[CardPile]):
    logger.debug(f">> ARGS: {locals()}")

    updated_count = CardInstance.objects.filter(team=team, pile__in=piles).update(pile=CardPile.DECK.value)

    return updated_count
