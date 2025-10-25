import logging
import uuid

from common.constants import GameStatus, GameType
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from game.models import Game, Team, TeamPlayerRelation
from game.services.error_codes import ErrorCode
from profile_game_master.models import GameMasterProfile
from profile_player.models import PlayerProfile
from profile_player.services.interfacer import svc_player_get_player_list_by_platform_user_ids

logger = logging.getLogger(__name__)


def svc_game_helper_run_validations_for_game_creation(request_data: dict) -> ErrorCode | None:
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("game_type"):
        return ErrorCode(ErrorCode.MISSING_GAME_TYPE)

    if not request_data.get("name"):
        return ErrorCode(ErrorCode.MISSING_NAME)

    if not request_data.get("description"):
        return ErrorCode(ErrorCode.MISSING_DESCRIPTION)

    try:
        GameType.tokentype_from_string(request_data["game_type"])
    except KeyError:
        return ErrorCode(ErrorCode.INVALID_GAME_TYPE, game_type=request_data["game_type"])

    return None


def svc_game_helper_run_validations_for_team_creation(request_data: dict) -> ErrorCode | None:
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("team_name"):
        return ErrorCode(ErrorCode.MISSING_TEAM_NAME)

    if not request_data.get("player_ids"):
        return ErrorCode(ErrorCode.MISSING_PLAYER_IDS)

    if not isinstance(request_data["player_ids"], list) or len(request_data["player_ids"]) == 0:
        return ErrorCode(ErrorCode.MISSING_PLAYER_IDS)

    return None


def svc_game_helper_get_game_type_from_request_data(request_data: dict) -> GameType:
    logger.debug(f">> ARGS: {locals()}")

    return GameType.tokentype_from_string(request_data["game_type"])


def svc_game_helper_get_players_from_request_data(request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    return svc_player_get_player_list_by_platform_user_ids(request_data["player_ids"])


# Collisions are rare so this should never go into long/infinite loop
def svc_game_helper_create_game(
    game_type: GameType, name: str, description: str, created_by: GameMasterProfile
) -> Game:
    logger.debug(f">> ARGS: {locals()}")

    try:
        game = Game.create(game_type=game_type, name=name, description=description, created_by=created_by)
        return game
    except IntegrityError:
        logger.warning(f"Duplicate game code generated while creating game for name: {name}")
        return svc_game_helper_create_game(
            game_type=game_type, name=name, description=description, created_by=created_by
        )


def svc_game_helper_get_games_for_game_master(request_data: dict, game_master: GameMasterProfile):
    logger.debug(f">> ARGS: {locals()}")

    games = Game.objects.all()

    if request_data.get("created_by_me", "False").lower() == "true":
        games = games.filter(created_by=game_master)

    games = games.order_by("-created")

    return games


def svc_game_helper_get_game_for_player(player: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    game_ids = TeamPlayerRelation.objects.filter(player=player).values_list("game", flat=True)
    games = Game.objects.filter(id__in=game_ids)

    return games


def svc_game_helper_get_game_by_id(game_id: str):
    logger.debug(f">> ARGS: {locals()}")

    try:
        game = Game.objects.get(external_id=game_id)
        return None, game
    except Game.DoesNotExist:
        return ErrorCode(ErrorCode.INVALID_GAME_ID, game_id=game_id), None


def svc_game_helper_start_game(game: Game):
    logger.debug(f">> ARGS: {locals()}")

    if game.game_status != GameStatus.PENDING.value:
        return (
            ErrorCode(
                ErrorCode.INVALID_GAME_STATE, game_state=GameStatus.get_string_for_type(GameStatus(game.game_status))
            ),
            None,
        )

    game.game_status = GameStatus.IN_PROGRESS.value
    game.save()

    return None, game


def svc_game_helper_end_game(game: Game):
    logger.debug(f">> ARGS: {locals()}")

    if game.game_status != GameStatus.IN_PROGRESS.value:
        return (
            ErrorCode(
                ErrorCode.INVALID_GAME_STATE, game_state=GameStatus.get_string_for_type(GameStatus(game.game_status))
            ),
            None,
        )

    game.game_status = GameStatus.COMPLETED.value
    game.save()

    return None, game


def svc_game_helper_create_team(game: Game, team_name: str, team_colour: str, players: list[PlayerProfile]):
    logger.debug(f">> ARGS: {locals()}")

    with transaction.atomic():
        try:
            team = Team.create(game=game, team_name=team_name, team_colour=team_colour)

            for player in players:
                TeamPlayerRelation.create(team=team, player=player)
        except IntegrityError as e:
            return ErrorCode(ErrorCode.ERROR_CREATING_TEAM, error=str(e)), None

    return None, team


def svc_game_helper_get_teams_for_game(game: Game):
    logger.debug(f">> ARGS: {locals()}")

    teams = Team.objects.filter(game=game)
    return teams


def svc_game_helper_get_teams_for_player(game: Game, player: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    team = TeamPlayerRelation.objects.get(player=player, game=game).team
    return team


def svc_game_helper_get_team_by_id(team_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    try:
        team = Team.objects.get(external_id=team_id)
        return None, team
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.INVALID_TEAM_ID, team_id=team_id), None


def svc_game_helper_verify_player_is_in_team(player: PlayerProfile, team: Team):
    logger.debug(f">> ARGS: {locals()}")

    try:
        rel = TeamPlayerRelation.objects.get(player=player, team=team)
        return None
    except ObjectDoesNotExist:
        return ErrorCode(
            ErrorCode.PLAYER_DOES_NOT_BELONG_TO_TEAM, profile_name=player.profile_name, team_name=team.team_name
        )
