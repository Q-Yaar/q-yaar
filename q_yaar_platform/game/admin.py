from django.contrib import admin

from .models import Game, Team, TeamPlayerRelation


class GameAdmin(admin.ModelAdmin):
    list_display = ("game_code", "game_type", "name", "game_status")
    list_filter = ("game_type", "game_status")
    search_fields = ["name"]  # Also searches by tags, as done in the overriden method
    readonly_fields = ("created_by",)


admin.site.register(Game, GameAdmin)


class TeamAdmin(admin.ModelAdmin):
    list_display = ("game", "team_name", "team_colour")
    search_fields = ["game__game_code", "external_id"]
    readonly_fields = ("game",)


admin.site.register(Team, TeamAdmin)


class TeamPlayerRelationAdmin(admin.ModelAdmin):
    list_display = ("team", "player", "game")
    search_fields = ["game__game_code", "player__profile_name", "player__platform_user__email"]
    readonly_fields = ("team", "player", "game")


admin.site.register(TeamPlayerRelation, TeamPlayerRelationAdmin)
