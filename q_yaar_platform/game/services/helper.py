import logging

from common.constants import GameType
from django.db import IntegrityError
from game.models import Game
from game.popo.teams_info import TeamInfoListConfig
from game.services.error_codes import ErrorCode
from profile_game_master.models import GameMasterProfile
from profile_player.models import PlayerProfile

logger = logging.getLogger(__name__)


def svc_game_helper_run_validations_for_game_creation(request_data: dict) -> ErrorCode | None:
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("game_type"):
        return ErrorCode(ErrorCode.MISSING_GAME_TYPE)

    if not request_data.get("name"):
        return ErrorCode(ErrorCode.MISSING_NAME)

    if not request_data.get("description"):
        return ErrorCode(ErrorCode.MISSING_DESCRIPTION)

    if not request_data.get("player_ids"):
        return ErrorCode(ErrorCode.MISSING_PLAYER_IDS)

    if not request_data.get("teams_info"):
        return ErrorCode(ErrorCode.MISSING_TEAMS_INFO)

    try:
        GameType.tokentype_from_string(request_data["game_type"])
    except KeyError:
        return ErrorCode(ErrorCode.INVALID_GAME_TYPE, game_type=request_data["game_type"])

    player_ids = PlayerProfile.objects.filter(platform_user__external_id__in=request_data["player_ids"]).values_list(
        "platform_user__external_id", flat=True
    )
    input_ids = set(request_data["player_ids"])
    fetched_ids = set()
    for player_id in player_ids:
        fetched_ids.add(str(player_id))

    invalid_ids = input_ids - fetched_ids
    if invalid_ids:
        return ErrorCode(ErrorCode.PLAYER_IDS_DO_NOT_EXIST, player_ids=list(invalid_ids))

    try:
        teams_info = TeamInfoListConfig.from_json(request_data["teams_info"])
    except Exception:
        return ErrorCode(ErrorCode.INVALID_TEAMS_INFO_FORMAT)

    return None


def svc_game_helper_get_game_type_from_request_data(request_data: dict) -> GameType:
    logger.debug(f">> ARGS: {locals()}")

    return GameType.tokentype_from_string(request_data["game_type"])


def svc_game_helper_get_players_from_request_data(request_data: dict) -> list[PlayerProfile]:
    logger.debug(f">> ARGS: {locals()}")

    return PlayerProfile.objects.filter(platform_user__external_id__in=request_data["player_ids"])


def svc_game_helper_get_teams_info_from_request_data(request_data: dict) -> TeamInfoListConfig:
    logger.debug(f">> ARGS: {locals()}")

    return TeamInfoListConfig.from_json(request_data["teams_info"])


# Collisions are rare so this should never go into long/infinite loop
def svc_game_helper_create_game(
    game_type: GameType,
    name: str,
    description: str,
    created_by: GameMasterProfile,
    players: list[PlayerProfile],
    teams_info: TeamInfoListConfig,
) -> Game:
    logger.debug(f">> ARGS: {locals()}")

    try:
        game = Game.create(
            game_type=game_type,
            name=name,
            description=description,
            created_by=created_by,
            players=players,
            teams_info=teams_info,
        )
        return game
    except IntegrityError:
        logger.warning(f"Duplicate game code generated while creating game for name: {name}")
        return svc_game_helper_create_game(name=name, description=description, created_by=created_by)


def svc_game_helper_get_games_for_game_master(request_data: dict, game_master: GameMasterProfile):
    logger.debug(f">> ARGS: {locals()}")

    games = Game.objects.all()

    if request_data.get("created_by_me", "False").lower() == "true":
        games = games.filter(created_by=game_master)

    games = games.order_by("-created")

    return games


def svc_game_helper_get_game_for_player(player: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    games = Game.objects.filter(players=player).order_by("-created")

    return games
