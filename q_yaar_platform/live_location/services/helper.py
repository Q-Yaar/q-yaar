import logging
import uuid

from common.constants import LocationClientType
from django.contrib.gis.geos import Point
from game.models import Game
from game.services.interfacer import svc_game_get_game_by_id
from live_location.api.serializers import LiveLocationSerializer, LocationSettingsSerializer
from live_location.models import LiveLocation, LocationSharingSetting
from live_location.parser.client import LocationParserClient
from live_location.parser.response_format import LocationResponseFormat
from profile_player.models import PlayerProfile

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


def svc_live_location_helper_run_validations_to_add_location(tracking_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    location_settings = LocationSharingSetting.objects.get(external_id=tracking_id)
    if not location_settings.is_sharing_enabled:
        return ErrorCode(ErrorCode.LOCATION_SHARING_DISABLED), None

    return None, location_settings


def svc_live_location_helper_validate_and_get_tracker_client(tracker_client: str):
    logger.debug(f">> ARGS: {locals()}")

    try:
        return None, LocationClientType.tokentype_from_string(tracker_client)
    except KeyError:
        return ErrorCode(ErrorCode.INVALID_TRACKER_CLIENT, tracker_client=tracker_client), None


def svc_live_location_helper_get_player_locations_for_game(game: Game):
    logger.debug(f">> ARGS: {locals()}")

    return (
        LiveLocation.objects.filter(
            player__teamplayerrelation__game=game, player__location_sharing_setting__is_sharing_enabled=True
        )
        .order_by("player_id", "-created")
        .distinct("player_id")
    )


def svc_live_location_helper_get_serialized_locations(
    locations: LiveLocation | list[LiveLocation], many: bool = False
):
    logger.debug(f">> ARGS: {locals()}")
    return LiveLocationSerializer(locations, many=many).data


def svc_live_location_helper_get_game_by_id(game_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_get_game_by_id(game_id=game_id)


def svc_live_location_helper_get_or_create_location_settings(player: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    return LocationSharingSetting.objects.get_or_create(player=player)[0]


def svc_live_location_helper_delete_location_settings(location_settings: LocationSharingSetting):
    logger.debug(f">> ARGS: {locals()}")

    location_settings.delete()


def svc_live_location_helper_get_serialized_location_settings(
    location_settings: LocationSharingSetting | list[LocationSharingSetting], many: bool = False
):
    logger.debug(f">> ARGS: {locals()}")

    return LocationSettingsSerializer(location_settings, many=many).data


def svc_live_location_helper_update_location_settings(location_settings: LocationSharingSetting, enabled: bool):
    logger.debug(f">> ARGS: {locals()}")

    location_settings.is_sharing_enabled = enabled
    location_settings.save()

    return location_settings


def svc_live_location_helper_parse_live_location_data(tracker_client: LocationClientType, request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    parser = LocationParserClient(client_type=tracker_client)

    try:
        return None, parser.parse(data=request_data)
    except KeyError as e:
        return ErrorCode(ErrorCode.UNABLE_TO_PARSE_LOCATION_DATA, error=repr(e)), None


def svc_live_location_helper_create_live_location(
    tracker_client: LocationClientType,
    location_settings: LocationSharingSetting,
    parsed_location_data: LocationResponseFormat,
):
    logger.debug(f">> ARGS: {locals()}")

    location_pnt = Point(x=parsed_location_data.lon, y=parsed_location_data.lat)

    live_location = LiveLocation.create(
        player=location_settings.player,
        location_pnt=location_pnt,
        accuracy=parsed_location_data.accuracy,
        client=tracker_client,
        tracking_meta=parsed_location_data.raw_data,
    )

    return live_location
