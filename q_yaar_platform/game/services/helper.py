import logging
import uuid

from common.constants import GameStatus, GameType, GameVisibilityMode, TeamType
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.db.models import Q, QuerySet
from game.models import Game, Team, TeamPlayerRelation
from game.services.error_codes import ErrorCode
from notification.tasks import send_notification
from profile_game_master.models import GameMasterProfile
from profile_player.models import PlayerProfile

logger = logging.getLogger(__name__)


def _svc_apply_filters_for_game_explore(games: QuerySet[Game], request_data: dict) -> QuerySet[Game]:
    logger.debug(f">> ARGS: {locals()}")

    if request_data.get("search"):
        search_query = request_data["search"]
        games = games.filter(Q(name__icontains=search_query) | Q(game_code__icontains=search_query))

    if request_data.get("game_type"):
        try:
            game_type = GameType.tokentype_from_string(request_data["game_type"])
            games = games.filter(game_type=game_type)
        except KeyError:
            pass

    if request_data.get("game_status"):
        try:
            game_status = GameStatus.tokentype_from_string(request_data["game_status"])
            games = games.filter(game_status=game_status)
        except KeyError:
            pass

    return games


def _svc_apply_filters_for_teams(teams: QuerySet[Team], request_data: dict) -> QuerySet[Team]:
    logger.debug(f">> ARGS: {locals()}")

    if request_data.get("team_type"):
        try:
            team_type = TeamType.tokentype_from_string(request_data["team_type"])
            teams = teams.filter(team_type=team_type)
        except KeyError:
            pass

    return teams


def svc_game_helper_get_player_ids_for_game(game: Game):
    logger.debug(f">> ARGS: {locals()}")

    return list(
        TeamPlayerRelation.objects.filter(game=game, team__team_type=TeamType.PLAYER.value).values_list(
            "player__platform_user__external_id", flat=True
        )
    )


def svc_game_helper_get_player_ids_for_team(team: Team):
    logger.debug(f">> ARGS: {locals()}")

    return list(
        TeamPlayerRelation.objects.filter(team=team).values_list("player__platform_user__external_id", flat=True)
    )


def svc_game_helper_get_player_ids_for_teams(teams: QuerySet[Team]):
    logger.debug(f">> ARGS: {locals()}")

    return list(
        TeamPlayerRelation.objects.filter(team__in=teams).values_list("player__platform_user__external_id", flat=True)
    )


def svc_game_helper_run_validations_for_game_creation(request_data: dict) -> ErrorCode | None:
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("game_type"):
        return ErrorCode(ErrorCode.MISSING_GAME_TYPE)

    if not request_data.get("game_visibility_mode"):
        return ErrorCode(ErrorCode.MISSING_GAME_VISIBILITY_MODE)

    if not request_data.get("name"):
        return ErrorCode(ErrorCode.MISSING_NAME)

    if not request_data.get("description"):
        return ErrorCode(ErrorCode.MISSING_DESCRIPTION)

    try:
        GameType.tokentype_from_string(request_data["game_type"])
    except KeyError:
        return ErrorCode(ErrorCode.INVALID_GAME_TYPE, game_type=request_data["game_type"])

    try:
        GameVisibilityMode.tokentype_from_string(request_data["game_visibility_mode"])
    except KeyError:
        return ErrorCode(
            ErrorCode.INVALID_GAME_VISIBILITY_MODE, game_visibility_mode=request_data["game_visibility_mode"]
        )
    return None


def svc_game_helper_run_validations_for_team_creation(request_data: dict) -> ErrorCode | None:
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("team_name"):
        return ErrorCode(ErrorCode.MISSING_TEAM_NAME)

    if not request_data.get("team_colour"):
        return ErrorCode(ErrorCode.MISSING_TEAM_COLOUR)

    return None


def svc_game_helper_run_validations_for_team_update(game: Game) -> ErrorCode | None:
    logger.debug(f">> ARGS: {locals()}")

    if game.game_status != GameStatus.PENDING.value:
        return ErrorCode(
            ErrorCode.INVALID_GAME_STATE, game_state=GameStatus.get_string_for_type(GameStatus(game.game_status))
        )

    return None


def svc_game_helper_run_validations_for_player_join(game: Game) -> ErrorCode | None:
    logger.debug(f">> ARGS: {locals()}")

    if game.game_status != GameStatus.PENDING.value:
        return ErrorCode(
            ErrorCode.INVALID_GAME_STATE, game_state=GameStatus.get_string_for_type(GameStatus(game.game_status))
        )

    return None


def svc_game_helper_run_validations_for_game_update(
    game: Game, profile: GameMasterProfile, request_data: dict
) -> ErrorCode | None:
    logger.debug(f">> ARGS: {locals()}")

    if game.game_status != GameStatus.PENDING.value:
        return ErrorCode(
            ErrorCode.INVALID_GAME_STATE, game_state=GameStatus.get_string_for_type(GameStatus(game.game_status))
        )
    if game.created_by != profile:
        return ErrorCode(ErrorCode.INVALID_GAME_UPDATER)

    if "game_visibility_mode" in request_data:
        try:
            GameVisibilityMode.tokentype_from_string(request_data["game_visibility_mode"])
        except KeyError:
            return ErrorCode(
                ErrorCode.INVALID_GAME_VISIBILITY_MODE, game_visibility_mode=request_data["game_visibility_mode"]
            )
    return None


def svc_game_helper_run_validations_for_kick_player(request_data: dict) -> ErrorCode | None:
    logger.debug(f">> ARGS: {locals()}")

    if not request_data.get("player_id"):
        return ErrorCode(ErrorCode.MISSING_PLAYER_ID)

    return None


def svc_game_helper_get_game_type_from_request_data(request_data: dict) -> GameType:
    logger.debug(f">> ARGS: {locals()}")

    return GameType.tokentype_from_string(request_data["game_type"])


def svc_game_helper_get_game_visibility_mode_from_request_data(request_data: dict) -> GameVisibilityMode:
    logger.debug(f">> ARGS: {locals()}")

    return GameVisibilityMode.tokentype_from_string(request_data["game_visibility_mode"])


# Collisions are rare so this should never go into long/infinite loop
def svc_game_helper_create_game(
    game_type: GameType,
    game_visibility_mode: GameVisibilityMode,
    name: str,
    description: str,
    created_by: GameMasterProfile,
) -> Game:
    logger.debug(f">> ARGS: {locals()}")

    try:
        game = Game.create(
            game_type=game_type,
            game_visibility_mode=game_visibility_mode,
            name=name,
            description=description,
            created_by=created_by,
        )

        Team.create(game=game, team_name="SPECTATORS", team_colour="Grey", team_type=TeamType.SPECTATOR)

        return game
    except IntegrityError:
        logger.warning(f"Duplicate game code generated while creating game for name: {name}")
        return svc_game_helper_create_game(
            game_type=game_type,
            game_visibility_mode=game_visibility_mode,
            name=name,
            description=description,
            created_by=created_by,
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
    games = Game.objects.filter(id__in=game_ids).order_by("-created")

    return games


def svc_game_helper_explore_games(player: PlayerProfile, request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    game_ids = TeamPlayerRelation.objects.filter(player=player).values_list("game", flat=True)
    games = (
        Game.objects.filter(game_visibility_mode=GameVisibilityMode.PUBLIC.value)
        .exclude(id__in=game_ids)
        .order_by("-created")
    )

    games = _svc_apply_filters_for_game_explore(games, request_data)

    return games


def svc_game_helper_get_game_by_id(game_id: str):
    logger.debug(f">> ARGS: {locals()}")

    try:
        game = Game.objects.get(external_id=game_id)
        return None, game
    except Game.DoesNotExist:
        return ErrorCode(ErrorCode.INVALID_GAME_ID, game_id=game_id), None


def svc_game_helper_get_game_by_code(game_code: str):
    logger.debug(f">> ARGS: {locals()}")

    try:
        game = Game.objects.get(game_code=game_code)
        return None, game
    except Game.DoesNotExist:
        return ErrorCode(ErrorCode.INVALID_GAME_ID, game_id=game_code), None


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

    player_ids = svc_game_helper_get_player_ids_for_game(game=game)

    for player_id in player_ids:
        send_notification.delay(
            user_id=str(player_id),
            title=f"Game #{game.game_code} Started",
            message=f"Game {game.name} has started",
            payload={},
        )

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

    player_ids = svc_game_helper_get_player_ids_for_game(game=game)

    for player_id in player_ids:
        send_notification.delay(
            user_id=str(player_id),
            title=f"Game #{game.game_code} Completed",
            message=f"Game {game.name} has ended",
            payload={},
        )

    return None, game


def svc_game_helper_create_team(game: Game, team_name: str, team_colour: str):
    logger.debug(f">> ARGS: {locals()}")

    return Team.create(game=game, team_name=team_name, team_colour=team_colour, team_type=TeamType.PLAYER)


def svc_game_helper_get_teams_for_game(game: Game, request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    teams = Team.objects.filter(game=game)

    teams = _svc_apply_filters_for_teams(teams, request_data)

    return teams


def svc_game_helper_get_teams_for_player(game: Game, player: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    try:
        team = TeamPlayerRelation.objects.get(player=player, game=game).team
        return None, team
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.PLAYER_DOES_NOT_BELONG_TO_ANY_TEAM, profile_name=player.profile_name), None


def svc_game_helper_get_team_by_id(team_id: uuid.UUID):
    logger.debug(f">> ARGS: {locals()}")

    try:
        team = Team.objects.get(external_id=team_id)
        return None, team
    except ObjectDoesNotExist:
        return ErrorCode(ErrorCode.INVALID_TEAM_ID, team_id=team_id), None


def svc_game_helper_verify_player_is_in_team(player: PlayerProfile, team: Team):
    logger.debug(f">> ARGS: {locals()}")

    if not TeamPlayerRelation.objects.filter(player=player, team=team).exists():
        return ErrorCode(
            ErrorCode.PLAYER_DOES_NOT_BELONG_TO_TEAM, profile_name=player.profile_name, team_name=team.team_name
        )

    return None


def svc_game_helper_verify_player_belongs_to_game(player: PlayerProfile, game: Game):
    logger.debug(f">> ARGS: {locals()}")

    if not TeamPlayerRelation.objects.filter(player=player, game=game).exists():
        return ErrorCode(
            ErrorCode.PLAYER_DOES_NOT_BELONG_TO_GAME, profile_name=player.profile_name, game_name=game.name
        )

    return None


def svc_game_helper_update_team(team: Team, request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if request_data.get("team_name"):
        team.team_name = request_data["team_name"]

    if request_data.get("team_colour"):
        team.team_colour = request_data["team_colour"]

    team.save()

    return team


def svc_game_helper_update_game(game: Game, request_data: dict):
    logger.debug(f">> ARGS: {locals()}")

    if request_data.get("game_name"):
        game.name = request_data["game_name"]

    if request_data.get("game_description"):
        game.description = request_data["game_description"]

    if request_data.get("game_visibility_mode"):
        game.game_visibility_mode = svc_game_helper_get_game_visibility_mode_from_request_data(request_data)

    game.save()

    return game


def svc_game_helper_join_team(game: Game, team: Team, player: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    with transaction.atomic():
        TeamPlayerRelation.objects.filter(game=game, player=player).delete()
        team_player_relation = TeamPlayerRelation.create(team=team, player=player)

    player_ids = svc_game_helper_get_player_ids_for_team(team=team)
    player_ids.remove(player.get_external_id())

    for player_id in player_ids:
        send_notification.delay(
            user_id=str(player_id),
            title=f"New Teammate Alert",
            message=f"{player.profile_name} has joined your team in {game.name}",
            payload={},
        )

    return team_player_relation


def svc_game_helper_get_spectator_team(game: Game):
    logger.debug(f">> ARGS: {locals()}")

    try:
        team = Team.objects.get(game=game, team_type=TeamType.SPECTATOR.value)
        return None, team
    except Team.DoesNotExist:
        return ErrorCode(ErrorCode.INVALID_TEAM_ID, team_id="spectator"), None


def svc_game_helper_leave_game(game: Game, player: PlayerProfile):
    logger.debug(f">> ARGS: {locals()}")

    try:
        relation = TeamPlayerRelation.objects.get(game=game, player=player)
    except TeamPlayerRelation.DoesNotExist:
        return ErrorCode(
            ErrorCode.PLAYER_DOES_NOT_BELONG_TO_GAME, profile_name=player.profile_name, game_name=game.name
        ), None

    if relation.team.team_type == TeamType.PLAYER.value:
        if game.game_status != GameStatus.PENDING.value:
            return ErrorCode(
                ErrorCode.INVALID_GAME_STATE, game_state=GameStatus.get_string_for_type(GameStatus(game.game_status))
            ), None

    relation.delete()
    return None, None


def svc_game_helper_kick_player(game: Game, player: PlayerProfile, profile: GameMasterProfile):
    logger.debug(f">> ARGS: {locals()}")

    if game.created_by != profile:
        return ErrorCode(ErrorCode.INVALID_GAME_UPDATER), None

    try:
        relation = TeamPlayerRelation.objects.get(game=game, player=player)
    except TeamPlayerRelation.DoesNotExist:
        return ErrorCode(
            ErrorCode.PLAYER_DOES_NOT_BELONG_TO_GAME, profile_name=player.profile_name, game_name=game.name
        ), None

    if relation.team.team_type == TeamType.SPECTATOR.value:
        return ErrorCode(ErrorCode.INVALID_TEAM_ID, team_id="Cannot kick spectator"), None

    relation.delete()
    return None, None

