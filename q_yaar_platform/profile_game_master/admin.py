from django.contrib import admin

from .models import GameMasterProfile


class GameMasterProfileAdmin(admin.ModelAdmin):
    list_display = ("platform_user", "profile_name", "is_suspended", "get_external_id")
    list_filter = ("is_suspended",)
    readonly_fields = ("platform_user",)
    search_fields = ["platform_user__external_id", "platform_user__phone", "profile_name"]


admin.site.register(GameMasterProfile, GameMasterProfileAdmin)
