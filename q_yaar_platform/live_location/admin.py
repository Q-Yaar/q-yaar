from django.contrib import admin

from .models import LocationSharingSetting


@admin.register(LocationSharingSetting)
class LocationSharingSettingAdmin(admin.ModelAdmin):
    list_display = ("player", "is_sharing_enabled")
    list_filter = ("is_sharing_enabled",)
    search_fields = ["player__profile_name", "player__platform_user__email", "player__platform_user__external_id"]
