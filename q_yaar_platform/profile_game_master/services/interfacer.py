import logging

from account.models import PlatformUser
from profile_game_master.models import GameMasterProfile
from .helper import (
    svc_game_master_helper_check_if_game_master_with_email_exists,
    svc_game_master_helper_create_game_master,
    svc_game_master_helper_get_game_master_for_platform_user,
    svc_game_master_helper_get_serialized_game_master,
    svc_game_master_helper_update_game_master,
)


logger = logging.getLogger(__name__)


def svc_game_master_get_game_master_for_platform_user(platform_user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_master_helper_get_game_master_for_platform_user(platform_user=platform_user)


def svc_game_master_get_serialized_game_master_profile(game_master: GameMasterProfile):
    logger.debug(f">> ARGS: {locals()}")

    return svc_game_master_helper_get_serialized_game_master(game_master=game_master)


def svc_game_master_create_game_master_for_platform_user(
    platform_user: PlatformUser, profile_name: str, profile_pic: str = {}, serialized: bool = False
):
    logger.debug(f">> ARGS: {locals()}")

    error, game_master = svc_game_master_helper_create_game_master(
        platform_user=platform_user, profile_name=profile_name, profile_pic=profile_pic
    )
    if error:
        return error, None

    if serialized:
        game_master = svc_game_master_helper_get_serialized_game_master(game_master=game_master)

    return None, game_master


def svc_game_master_update_game_master(profile: GameMasterProfile, request_data: dict, serialized: bool = False):
    logger.debug(f">> ARGS: {locals()}")

    profile = svc_game_master_helper_update_game_master(game_master=profile, request_data=request_data)

    if serialized:
        profile = svc_game_master_helper_get_serialized_game_master(game_master=profile)

    return profile


def svc_game_master_check_if_game_master_with_email_exists(email: str):
    return svc_game_master_helper_check_if_game_master_with_email_exists(email=email)
