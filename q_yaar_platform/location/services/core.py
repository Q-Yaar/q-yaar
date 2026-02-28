import logging

from location.popo.location_meta import LocationAddData
from profile_player.models import PlayerProfile

from .error_codes import ErrorCode
from .helper import (
    svc_location_helper_apply_filters,
    svc_location_helper_create_location_points,
    svc_location_helper_enable_sharing,
    svc_location_helper_get_last_location,
    svc_location_helper_get_player_by_id,
    svc_location_helper_get_serialized_locations,
    svc_location_helper_get_serialized_setting,
    svc_location_helper_get_sharing_setting,
    svc_location_helper_reset_setting,
    svc_location_helper_run_validations_to_add_location,
    svc_location_helper_run_validations_to_get_locations,
    svc_location_helper_update_tracking_code,
    svc_location_helper_validate_and_get_game,
    svc_location_helper_validate_and_get_team,
)
from location.models import Location


logger = logging.getLogger(__name__)


def svc_location_add_location(player: PlayerProfile, request_data: dict, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_location_helper_run_validations_to_add_location(request_data)
    if error:
        return error, None
    
    from location.popo.location_meta import LocationPointData
    location_add_data = LocationAddData(
        game_id=request_data.get("game_id"),
        team_id=request_data.get("team_id"),
        client=request_data.get("client"),
        locations=[LocationPointData(**pt) for pt in request_data.get("locations", [])]
    )

    error, game = svc_location_helper_validate_and_get_game(location_add_data.game_id)
    if error:
        return error, None

    error, team = svc_location_helper_validate_and_get_team(location_add_data.team_id)
    if error:
        return error, None

    locations = svc_location_helper_create_location_points(
        player=player, game=game, team=team, location_data=location_add_data
    )

    if serialized:
        locations = svc_location_helper_get_serialized_locations(locations, many=True)

    return ErrorCode(ErrorCode.CREATED), locations


def svc_location_get_last_location(player_id: str, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error, player = svc_location_helper_get_player_by_id(player_id)
    if error:
        return error, None

    setting = svc_location_helper_get_sharing_setting(player)
    if not setting.is_sharing_enabled:
        return ErrorCode(ErrorCode.LOCATION_SHARING_DISABLED), None

    location = svc_location_helper_get_last_location(player)

    if serialized and location:
        location = svc_location_helper_get_serialized_locations(location, many=False)
    elif serialized and not location:
        location = {}

    return ErrorCode(ErrorCode.SUCCESS), location


def svc_location_get_locations(request_data: dict, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    error = svc_location_helper_run_validations_to_get_locations(request_data)
    if error:
        return error, None

    locations = Location.objects.all()

    error, locations = svc_location_helper_apply_filters(request_data, locations)
    if error:
        return error, None

    # Filter out locations for players who do not have sharing enabled
    locations = locations.filter(player__location_sharing_setting__is_sharing_enabled=True)

    locations = locations.order_by("-timestamp")

    if serialized:
        locations = svc_location_helper_get_serialized_locations(locations, many=True)

    return ErrorCode(ErrorCode.SUCCESS), locations


def svc_location_enable_sharing(player: PlayerProfile, request_data: dict, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    enable = request_data.get("is_sharing_enabled", False)
    setting = svc_location_helper_get_sharing_setting(player)
    setting = svc_location_helper_enable_sharing(setting, enable)

    if serialized:
        setting = svc_location_helper_get_serialized_setting(setting)

    return ErrorCode(ErrorCode.SUCCESS), setting


def svc_location_get_current_sharing_setting(player: PlayerProfile, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    setting = svc_location_helper_get_sharing_setting(player)

    if serialized:
        setting = svc_location_helper_get_serialized_setting(setting)

    return ErrorCode(ErrorCode.SUCCESS), setting



def svc_location_update_tracking_code(player: PlayerProfile, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    setting = svc_location_helper_get_sharing_setting(player)
    setting = svc_location_helper_update_tracking_code(setting)

    if serialized:
        setting = svc_location_helper_get_serialized_setting(setting)

    return ErrorCode(ErrorCode.SUCCESS), setting


def svc_location_reset_sharing_setting(player: PlayerProfile, serialized: bool = True):
    logger.debug(f">> ARGS: {locals()}")

    setting = svc_location_helper_get_sharing_setting(player)
    setting = svc_location_helper_reset_setting(setting)

    if serialized:
        setting = svc_location_helper_get_serialized_setting(setting)

    return ErrorCode(ErrorCode.SUCCESS), setting

