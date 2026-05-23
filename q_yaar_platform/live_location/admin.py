from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import LiveLocation, LocationSharingSetting


@admin.register(LocationSharingSetting)
class LocationSharingSettingAdmin(admin.ModelAdmin):
    list_display = ("player", "is_sharing_enabled")
    list_filter = ("is_sharing_enabled",)
    search_fields = ["player__profile_name", "player__platform_user__email", "player__platform_user__external_id"]


@admin.register(LiveLocation)
class LiveLocationAdmin(admin.ModelAdmin):
    list_display = ("player", "client", "location_pnt", "accuracy", "created")
    list_filter = ("client",)
    search_fields = ["player__profile_name", "player__platform_user__email", "player__platform_user__external_id"]
    readonly_fields = ("google_map", "location_pnt", "created", "modified")
    fields = ("player", "client", "accuracy", "location_pnt", "google_map", "info", "created", "modified")

    def google_map(self, obj):
        if obj.location_pnt:
            lat = obj.location_pnt.y
            lng = obj.location_pnt.x
            html = (
                f'<iframe width="600" height="400" frameborder="0" style="border:0" '
                f'src="https://maps.google.com/maps?q={lat},{lng}&z=15&output=embed" allowfullscreen></iframe>'
            )
            return mark_safe(html)
        return "No Location"
    google_map.short_description = "Google Map Location"

