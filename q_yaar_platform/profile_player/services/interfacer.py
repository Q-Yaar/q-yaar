import logging
import uuid

from account.models import PlatformUser
from profile_player.models import PlayerProfile

from .helper import (
    svc_player_helper_check_if_player_with_email_exists,
    svc_player_helper_create_player,
    svc_player_helper_get_player_for_platform_user,
    svc_player_helper_get_player_for_user_id,
    svc_player_helper_get_players_for_user_ids,
    svc_player_helper_get_serialized_player,
    svc_player_helper_update_player,
)

logger = logging.getLogger(__name__)


def svc_player_get_player_for_platform_user(platform_user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    return svc_player_helper_get_player_for_platform_user(platform_user=platform_user)


def svc_player_get_serialized_player_profile(player: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    return svc_player_helper_get_serialized_player(player=player)


def svc_player_create_player_for_platform_user(
    platform_user: PlatformUser, profile_name: str, profile_pic: str = {}, serialized: bool = False
):
    logger.debug(f">> ARGS: {locals()}")

    error, player = svc_player_helper_create_player(
        platform_user=platform_user, profile_name=profile_name, profile_pic=profile_pic
    )
    if error:
        return error, None

    if serialized:
        player = svc_player_helper_get_serialized_player(player=player)

    return None, player


def svc_player_update_player(profile: PlayerProfile, request_data: dict, serialized: bool = False):
    logger.debug(f">> ARGS: {locals()}")

    profile = svc_player_helper_update_player(player=profile, request_data=request_data)

    if serialized:
        profile = svc_player_helper_get_serialized_player(player=profile)

    return profile


def svc_player_check_if_player_with_email_exists(email: str):
    logger.debug(f">> ARGS: {locals()}")
    return svc_player_helper_check_if_player_with_email_exists(email=email)


def svc_player_get_player_by_platform_user_id(user_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")
    return svc_player_helper_get_player_for_user_id(user_id=user_id)


def svc_player_get_player_list_by_platform_user_ids(user_ids: list[uuid.UUID]):
    logger.debug(f">> ARGS: {locals()}")
    return svc_player_helper_get_players_for_user_ids(user_ids=user_ids)
