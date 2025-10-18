import logging
import uuid

import jwt
from account.models import PlatformUser
from account.services.interfacer import (
    svc_account_check_if_user_with_email_exists,
    svc_account_get_or_create_platform_user,
    svc_account_get_platform_user_by_email,
    svc_account_get_platform_user_by_id,
    svc_account_get_serialized_platform_user,
)
from common.constants import UserRolesType
from common.phonenumber import is_valid_indian_number
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from jwt_auth.authentication import JWTRefreshToken
from profile_game_master.services.interfacer import (
    svc_game_master_check_if_game_master_with_email_exists,
    svc_game_master_create_game_master_for_platform_user,
    svc_game_master_get_game_master_for_platform_user,
    svc_game_master_get_serialized_game_master_profile,
    svc_game_master_update_game_master,
)
from profile_player.models import PlayerProfile
from profile_player.services.interfacer import (
    svc_player_check_if_player_with_email_exists,
    svc_player_create_player_for_platform_user,
    svc_player_get_player_for_platform_user,
    svc_player_get_serialized_player_profile,
    svc_player_update_player,
)

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)


######################################################################################################################
##########################################   PRIVATE FUNCTIONS   #####################################################
######################################################################################################################


def _svc_run_basic_user_validations(request_data: dict):
    logger.debug(">>")  # Not logging locals since password will get logged

    if not request_data.get("email"):
        return ErrorCode(ErrorCode.MISSING_EMAIL)

    if not request_data.get("password"):
        return ErrorCode(ErrorCode.MISSING_PASSWORD)

    return None


def _svc_validate_email(email: str):
    logger.debug(f">> ARGS: {locals()}")

    try:
        validate_email(email)
    except ValidationError:
        return ErrorCode(ErrorCode.INVALID_EMAIL, email=email)

    return None


def _svc_get_auth_tokens_for_user(platform_user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    refresh_token = JWTRefreshToken.for_user(user=platform_user)
    access_token = refresh_token.access_token

    return str(access_token), str(refresh_token)


def _svc_get_auth_tokens_for_profile(platform_user: PlatformUser, role: UserRolesType):
    logger.debug(f">> ARGS: {locals()}")

    refresh_token = JWTRefreshToken.for_user(user=platform_user, role=UserRolesType.get_string_for_type(role))
    access_token = refresh_token.access_token

    return str(access_token), str(refresh_token)


def _svc_get_serialized_player_profile(player: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    return svc_player_get_serialized_player_profile(player=player)


def _svc_get_all_serialized_roles_for_user(platform_user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    profiles = {}

    error, player = svc_player_get_player_for_platform_user(platform_user=platform_user)
    if player:
        access_token, refresh_token = _svc_get_auth_tokens_for_profile(
            platform_user=platform_user, role=UserRolesType.PLAYER
        )
        profiles[UserRolesType.get_string_for_type(UserRolesType.PLAYER)] = {
            "data": _svc_get_serialized_player_profile(player=player),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    error, game_master = svc_game_master_get_game_master_for_platform_user(platform_user=platform_user)
    if game_master:
        access_token, refresh_token = _svc_get_auth_tokens_for_profile(
            platform_user=platform_user, role=UserRolesType.GAME_MASTER
        )
        profiles[UserRolesType.get_string_for_type(UserRolesType.GAME_MASTER)] = {
            "data": svc_game_master_get_serialized_game_master_profile(game_master=game_master),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    return profiles


######################################################################################################################
########################################   PRIVATE FUNCTIONS END   ###################################################
######################################################################################################################


def svc_auth_helper_run_validations_for_user_login(request_data: dict):
    logger.debug(">>")  # Not logging locals since password will get logged

    return _svc_run_basic_user_validations(request_data=request_data)


def svc_auth_helper_run_validations_for_user_sign_up(request_data: dict):
    logger.debug(">>")  # Not logging locals since password will get logged

    error = _svc_run_basic_user_validations(request_data=request_data)
    if error:
        return error

    error = _svc_validate_email(email=request_data["email"])
    if error:
        return error

    if not request_data.get("role"):
        return ErrorCode(ErrorCode.MISSING_ROLE)

    if not request_data.get("profile_name"):
        return ErrorCode(ErrorCode.MISSING_PROFILE_NAME)

    if not request_data.get("confirm_password"):
        return ErrorCode(ErrorCode.MISSING_CONFIRM_PASSWORD)

    if request_data["password"] != request_data["confirm_password"]:
        return ErrorCode(ErrorCode.PASSWORDS_DO_NOT_MATCH)

    return None


def svc_auth_helper_run_validations_to_check_user_and_profile_exists(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("email"):
        return ErrorCode(ErrorCode.MISSING_EMAIL)

    if not request_data.get("role"):
        return ErrorCode(ErrorCode.MISSING_ROLE)

    return None


def svc_auth_helper_run_validations_to_refresh_token(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("refresh_token"):
        return ErrorCode(ErrorCode.MISSING_TOKEN)

    if not request_data.get("user_id"):
        return ErrorCode(ErrorCode.MISSING_USER_ID)

    return None


def svc_auth_helper_run_validations_to_update_password(request_data: dict):
    logger.debug(">>")  # Not logging locals since password will get logged

    if not request_data.get("password"):
        return ErrorCode(ErrorCode.MISSING_PASSWORD)

    return None


def svc_auth_helper_validate_and_get_user_from_email(email: str):
    logger.debug(f">> ARGS: {locals()}")

    return svc_account_get_platform_user_by_email(email=email)


def svc_auth_helper_validate_and_get_user_by_id(user_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    return svc_account_get_platform_user_by_id(user_id=user_id)


def svc_auth_helper_validate_and_get_role(role: str):
    logger.debug(f">> ARGS: {locals()}")

    try:
        return None, UserRolesType.tokentype_from_string(role)
    except KeyError:
        return ErrorCode(ErrorCode.INVALID_ROLE, role=role), None


def svc_auth_helper_check_account_is_active(platform_user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    if not platform_user.is_active:
        return ErrorCode(ErrorCode.ACCOUNT_DEACTIVATED)

    if platform_user.is_suspended:
        return ErrorCode(ErrorCode.ACCOUNT_SUSPENDED)

    if platform_user.is_deleted:
        return ErrorCode(ErrorCode.ACCOUNT_DELETED)

    return None


def svc_auth_helper_check_password_for_user(platform_user: PlatformUser, password: str):
    logger.debug(">>")  # Not logging locals since password will get logged

    if not platform_user.check_password(password):
        return ErrorCode(ErrorCode.INVALID_PASSWORD)

    return None


def svc_auth_helper_get_user_token_for_platform_user(platform_user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    return _svc_get_auth_tokens_for_user(platform_user=platform_user)


def svc_auth_helper_get_serialized_jwt_token(access_token, refresh_token: str, platform_user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "data": svc_account_get_serialized_platform_user(platform_user=platform_user),
    }


def svc_auth_helper_validate_and_get_phone_number(phone: str):
    logger.debug(f">> ARGS: {locals()}")

    is_valid, parsed_e164, phone_number = is_valid_indian_number(mob_num=phone)

    if not is_valid:
        return ErrorCode(ErrorCode.INVALID_PHONE, phone=phone), None

    return None, parsed_e164


def svc_auth_helper_get_or_create_new_user(email: str, password: str, phone: str = None):
    logger.debug(">>")  # Not logging locals since password will get logged

    return svc_account_get_or_create_platform_user(email=email, password=password, phone=phone)


def svc_auth_helper_check_user_exists(email: str):
    logger.debug(f">> ARGS: {locals()}")

    return svc_account_check_if_user_with_email_exists(email=email)


def svc_auth_helper_check_profile_exists(email: str, role: UserRolesType):
    logger.debug(f">> ARGS: {locals()}")

    PROFILE_CHECK_MAP = {
        UserRolesType.PLAYER: svc_player_check_if_player_with_email_exists,
        UserRolesType.GAME_MASTER: svc_game_master_check_if_game_master_with_email_exists,
    }

    return PROFILE_CHECK_MAP[role](email=email)


def svc_auth_helper_get_serialized_user_and_profile_exists(user_exists: bool, profile_exists: bool):
    logger.debug(f">> ARGS: {locals()}")

    return {"user_exists": user_exists, "profile_exists": profile_exists}


def svc_auth_helper_get_token_and_user_for_token_refresh(refresh_token: str, platform_user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    try:
        decoded_token = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.DecodeError:
        return ErrorCode(ErrorCode.INVALID_JWT_TOKEN, error="Invalid JWT token"), None, None
    except jwt.ExpiredSignatureError:
        return ErrorCode(ErrorCode.INVALID_JWT_TOKEN, error="Token expired"), None, None
    except jwt.InvalidTokenError:
        return ErrorCode(ErrorCode.INVALID_JWT_TOKEN, error="Invalid JWT token"), None, None

    if platform_user.email != decoded_token.get("email"):
        return ErrorCode(ErrorCode.INVALID_JWT_TOKEN, error="Token does not belong to user"), None, None

    access_token, refresh_token = svc_auth_helper_get_user_token_for_platform_user(platform_user=platform_user)

    return None, access_token, refresh_token


def svc_auth_helper_get_serialized_refresh_token(access_token: str, refresh_token: str, platform_user: PlatformUser):
    logger.debug(f">> ARGS: {locals()}")

    return {
        "user": svc_auth_helper_get_serialized_jwt_token(
            access_token=access_token, refresh_token=refresh_token, platform_user=platform_user
        ),
        "profiles": _svc_get_all_serialized_roles_for_user(platform_user=platform_user),
    }


def svc_auth_helper_create_profile_for_user(
    platform_user: PlatformUser,
    role: UserRolesType,
    profile_name: str,
    profile_pic: dict = {},
    serialized: bool = False,
):
    logger.debug(f">> ARGS: {locals()}")

    ROLE_CREATE_MAP = {
        UserRolesType.PLAYER: svc_player_create_player_for_platform_user,
        UserRolesType.GAME_MASTER: svc_game_master_create_game_master_for_platform_user,
    }

    return ROLE_CREATE_MAP[role](
        platform_user=platform_user, profile_name=profile_name, profile_pic=profile_pic, serialized=serialized
    )


def svc_auth_helper_get_profile_for_user_and_role(platform_user: PlatformUser, role: UserRolesType):
    logger.debug(f">> ARGS: {locals()}")

    if not role:
        return None, None

    ROLE_GET_MAP = {
        UserRolesType.PLAYER: svc_player_get_player_for_platform_user,
        UserRolesType.GAME_MASTER: svc_game_master_get_game_master_for_platform_user,
    }

    return ROLE_GET_MAP[role](platform_user=platform_user)


def svc_auth_helper_update_profile(
    request_data: dict, profile: PlayerProfile, role: UserRolesType, serialized: bool = True
):
    logger.debug(f">> ARGS: {locals()}")

    ROLE_UPDATE_TYPE_MAP = {
        UserRolesType.PLAYER: svc_player_update_player,
        UserRolesType.GAME_MASTER: svc_game_master_update_game_master,
    }

    return ROLE_UPDATE_TYPE_MAP[role](profile=profile, request_data=request_data, serialized=serialized)


def svc_auth_helper_update_password(platform_user: PlatformUser, password: str):
    logger.debug(">>")  # Not logging locals since password will get logged

    platform_user.set_password(password)
    platform_user.save()

    return platform_user


def svc_auth_helper_get_serialized_user_for_signup(
    platform_user: PlatformUser, role: UserRolesType, profile: PlayerProfile
):
    logger.debug(f">> ARGS: {locals()}")

    return {
        "user": svc_account_get_serialized_platform_user(platform_user=platform_user),
        "profiles": {UserRolesType.get_string_for_type(role): _svc_get_serialized_player_profile(player=profile)},
    }
