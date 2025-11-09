import logging
import uuid

from account.models import PlatformUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from profile_player.api.serializers import PlayerProfileSerializer
from profile_player.models import PlayerProfile

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


def svc_player_helper_get_player_for_platform_user(platform_user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    try:
        return None, PlayerProfile.objects.get(platform_user=platform_user)
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.PLAYER_DOES_NOT_EXIST, user_id=str(platform_user.get_external_id())), None


def svc_player_helper_get_player_for_user_id(user_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    try:
        return None, PlayerProfile.objects.get(platform_user__external_id=user_id)
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.PLAYER_DOES_NOT_EXIST, user_id=str(user_id)), None


def svc_player_helper_get_players_for_user_ids(user_ids: list[uuid.UUID]):
    logger.debug(f">> ARGS: {locals()}")

    players = PlayerProfile.objects.filter(platform_user__external_id__in=user_ids)

    extracted_ids = players.values_list("platform_user__external_id", flat=True)
    invalid_ids = set(str(user_id) for user_id in user_ids) - set(str(pid) for pid in extracted_ids)

    if invalid_ids:
        return ErrorCode(ErrorCode.INVALID_PLAYER_IDS, invalid_ids=list(invalid_ids)), None

    return None, players


def svc_player_helper_get_serialized_player(player: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    return PlayerProfileSerializer(player, many=False).data


def svc_player_helper_create_player(platform_user: PlatformUser, profile_name: str, profile_pic: dict = {}):
    logger.debug(f">> ARGS: {locals()}")

    try:
        player = PlayerProfile.create(platform_user=platform_user, profile_name=profile_name, profile_pic=profile_pic)
    except IntegrityError:
        return ErrorCode(ErrorCode.PLAYER_ALREADY_ONBOARDED, user_id=str(platform_user.get_external_id())), None

    return None, player


def svc_player_helper_update_player(player: PlayerProfile, request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if request_data.get("profile_name"):
        player.set_profile_name(request_data["profile_name"])

    if request_data.get("profile_pic"):
        player.set_profile_pic(profile_pic=request_data["profile_pic"])

    player.save()
    return player


def svc_player_helper_check_if_player_with_email_exists(email: str):
    logger.debug(f">> ARGS: {locals()}")

    return PlayerProfile.objects.filter(platform_user__email=email).exists()
