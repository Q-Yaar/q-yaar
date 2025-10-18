from django.contrib import admin

from .models import Game


class GameAdmin(admin.ModelAdmin):
    list_display = ("game_code", "game_type", "name", "game_status")
    list_filter = ("game_type", "game_status")
    search_fields = ["name"]  # Also searches by tags, as done in the overriden method
    readonly_fields = ("created_by",)


admin.site.register(Game, GameAdmin)
