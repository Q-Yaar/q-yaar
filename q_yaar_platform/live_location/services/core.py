import logging
import uuid

from live_location.services.helper import (
    svc_live_location_helper_create_live_location,
    svc_live_location_helper_delete_location_settings,
    svc_live_location_helper_get_game_by_id,
    svc_live_location_helper_get_or_create_location_settings,
    svc_live_location_helper_get_player_locations_for_game,
    svc_live_location_helper_get_serialized_location_settings,
    svc_live_location_helper_get_serialized_locations,
    svc_live_location_helper_parse_live_location_data,
    svc_live_location_helper_run_validations_to_add_location,
    svc_live_location_helper_update_location_settings,
    svc_live_location_helper_validate_and_get_tracker_client,
)
from profile_player.models import PlayerProfile

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


def svc_live_location_get_last_locations(game_id: uuid.UUID, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, game = svc_live_location_helper_get_game_by_id(game_id=game_id)
    if error:
        return error, None

    locations = svc_live_location_helper_get_player_locations_for_game(game=game)

    if serialized:
        locations = svc_live_location_helper_get_serialized_locations(locations, many=True)

    return ErrorCode(ErrorCode.SUCCESS), locations


def svc_live_location_get_location_settings(player: PlayerProfile, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    settings = svc_live_location_helper_get_or_create_location_settings(player=player)

    if serialized:
        settings = svc_live_location_helper_get_serialized_location_settings(settings, many=False)

    return ErrorCode(ErrorCode.SUCCESS), settings


def svc_live_location_delete_location_settings(player: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    settings = svc_live_location_helper_get_or_create_location_settings(player=player)
    svc_live_location_helper_delete_location_settings(settings)

    return ErrorCode(ErrorCode.NO_CONTENT), None


def svc_live_location_enable_location_sharing(player: PlayerProfile, enabled: bool, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    settings = svc_live_location_helper_get_or_create_location_settings(player=player)

    settings = svc_live_location_helper_update_location_settings(settings, enabled=enabled)

    if serialized:
        settings = svc_live_location_helper_get_serialized_location_settings(settings, many=False)

    return ErrorCode(ErrorCode.SUCCESS), settings


def svc_live_location_add_location_ping(
    tracker_client: str, tracking_id: uuid.UUID, request_data: dict, serialized: bool = True
):
    logger.debug(f">> ARGS: {locals()}")

    error, tracker_client = svc_live_location_helper_validate_and_get_tracker_client(tracker_client=tracker_client)
    if error:
        return error, None

    error, location_settings = svc_live_location_helper_run_validations_to_add_location(tracking_id=tracking_id)
    if error:
        return error, None

    error, parsed_location_data = svc_live_location_helper_parse_live_location_data(
        tracker_client=tracker_client, request_data=request_data
    )
    if error:
        return error, None

    live_location = svc_live_location_helper_create_live_location(
        tracker_client=tracker_client, location_settings=location_settings, parsed_location_data=parsed_location_data
    )

    if serialized:
        live_location = svc_live_location_helper_get_serialized_locations(live_location, many=False)

    return ErrorCode(ErrorCode.CREATED), live_location
