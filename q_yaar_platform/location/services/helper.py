import logging
import uuid
import string
import random
from django.db.models import ObjectDoesNotExist
from common.constants import Length
from game.models import Game, Team
from game.services.interfacer import svc_game_get_game_by_id, svc_game_get_team_by_id
from profile_player.models import PlayerProfile
from location.models import Location, LocationSharingSetting
from location.popo.location_meta import LocationAddData, LocationPointData
from location.api.serializers import LocationResponseSerializer, LocationSharingSettingSerializer
from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


def generate_tracking_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=Length.TRACKING_CODE))


def get_unique_tracking_code() -> str:
    while True:
        code = generate_tracking_code()
        if not LocationSharingSetting.objects.filter(tracking_code=code).exists():
            return code


def svc_location_helper_run_validations_to_add_location(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")
    
    locations = request_data.get("locations", [])
    if not locations:
        return ErrorCode(ErrorCode.MISSING_LOCATION_INPUT)
    
    return None


def svc_location_helper_run_validations_to_get_locations(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")
    
    if not request_data.get("game_id") and not request_data.get("team_id") and not request_data.get("player_id"):
        return ErrorCode(ErrorCode.MISSING_FILTER)
    
    return None


def svc_location_helper_validate_and_get_game(game_id: str | uuid.UUID | None):
    logger.debug(f">> ARGS: {locals()}")
    if not game_id:
        return None, None
    return svc_game_get_game_by_id(game_id)


def svc_location_helper_validate_and_get_team(team_id: str | uuid.UUID | None):
    logger.debug(f">> ARGS: {locals()}")
    if not team_id:
        return None, None
    return svc_game_get_team_by_id(team_id)


def svc_location_helper_get_player_by_id(player_id: str | uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")
    try:
        player = PlayerProfile.objects.get(platform_user__external_id=player_id)
        return None, player
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.LOCATION_SHARING_DISABLED), None


def svc_location_helper_get_sharing_setting(player: PlayerProfile) -> LocationSharingSetting:
    logger.debug(f">> ARGS: {locals()}")
    setting, _ = LocationSharingSetting.objects.get_or_create(player=player)
    return setting


def svc_location_helper_create_location_points(
    player: PlayerProfile, game: Game, team: Team, location_data: LocationAddData
) -> list[Location]:
    logger.debug(f">> ARGS: {locals()}")
    
    locations = []
    for point in location_data.locations:
        loc = Location.create(
            player=player,
            game=game,
            team=team,
            lat=point.lat,
            lon=point.lon,
            reported_time=point.reported_time,
            accuracy=point.accuracy,
            client=location_data.client,
        )
        locations.append(loc)
        
    return locations


def svc_location_helper_get_last_location(player: PlayerProfile) -> Location | None:
    logger.debug(f">> ARGS: {locals()}")
    return Location.objects.filter(player=player).order_by("-reported_time").first()


def svc_location_helper_apply_filters(request_data: dict, locations):
    logger.debug(f">> ARGS: {locals()}")
    
    if request_data.get("game_id"):
        error, game = svc_location_helper_validate_and_get_game(request_data["game_id"])
        if error:
            return error, None
        locations = locations.filter(game=game)

    if request_data.get("team_id"):
        error, team = svc_location_helper_validate_and_get_team(request_data["team_id"])
        if error:
            return error, None
        locations = locations.filter(team=team)
        
    if request_data.get("player_id"):
        error, player = svc_location_helper_get_player_by_id(request_data["player_id"])
        if error:
            return error, None
        locations = locations.filter(player=player)

    return None, locations


def svc_location_helper_get_serialized_locations(locations: Location | list[Location], many: bool):
    logger.debug(f">> ARGS: {locals()}")
    return LocationResponseSerializer(locations, many=many).data


def svc_location_helper_get_serialized_setting(setting: LocationSharingSetting):
    logger.debug(f">> ARGS: {locals()}")
    return LocationSharingSettingSerializer(setting).data


def svc_location_helper_update_tracking_code(setting: LocationSharingSetting) -> LocationSharingSetting:
    logger.debug(f">> ARGS: {locals()}")
    code = get_unique_tracking_code()
    setting.tracking_code = code
    setting.save()
    return setting


def svc_location_helper_enable_sharing(setting: LocationSharingSetting, enable: bool) -> LocationSharingSetting:
    logger.debug(f">> ARGS: {locals()}")
    setting.is_sharing_enabled = enable
    if enable and not setting.tracking_code:
        setting.tracking_code = get_unique_tracking_code()
    setting.save()
    return setting
