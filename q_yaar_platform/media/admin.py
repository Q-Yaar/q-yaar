from django.contrib import admin

from .models import Asset


class AssetAdmin(admin.ModelAdmin):
    list_display = ("external_id", "game", "role", "status", "asset_name")
    search_fields = ["external_id", "object_key", "asset_name", "game__game_code", "game__name"]
    list_filter = ("role", "status")
    readonly_fields = ("external_id", "object_key", "uploaded_by", "game", "role", "created", "modified")


admin.site.register(Asset, AssetAdmin)
