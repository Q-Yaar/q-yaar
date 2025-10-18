import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from account.models import PlatformUser
from profile_game_master.api.serializers import GameMasterProfileSerializer
from profile_game_master.models import GameMasterProfile
from .error_codes import ErrorCode


logger = logging.getLogger(__name__)


def svc_game_master_helper_get_game_master_for_platform_user(platform_user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    try:
        return None, GameMasterProfile.objects.get(platform_user=platform_user)
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.GAME_MASTER_DOES_NOT_EXIST, user_id=str(platform_user.get_external_id())), None


def svc_game_master_helper_get_serialized_game_master(game_master: GameMasterProfile):
    logger.debug(f">> ARGS: {locals()}")

    return GameMasterProfileSerializer(game_master, many=False).data


def svc_game_master_helper_create_game_master(platform_user: PlatformUser, profile_name: str, profile_pic: dict = {}):
    logger.debug(f">> ARGS: {locals()}")

    try:
        game_master = GameMasterProfile.create(
            platform_user=platform_user, profile_name=profile_name, profile_pic=profile_pic
        )
    except IntegrityError:
        return ErrorCode(ErrorCode.GAME_MASTER_ALREADY_ONBOARDED, user_id=str(platform_user.get_external_id())), None

    return None, game_master


def svc_game_master_helper_update_game_master(game_master: GameMasterProfile, request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if request_data.get("profile_name"):
        game_master.set_profile_name(request_data["profile_name"])

    if request_data.get("profile_pic"):
        game_master.set_profile_pic(profile_pic=request_data["profile_pic"])

    game_master.save()
    return game_master


def svc_game_master_helper_check_if_game_master_with_email_exists(email: str):
    logger.debug(f">> ARGS: {locals()}")

    return GameMasterProfile.objects.filter(platform_user__email=email).exists()
