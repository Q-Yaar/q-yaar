from django.contrib import admin

from .models import PushNotificationHistory


class PushNotificationHistoryAdmin(admin.ModelAdmin):
    list_display = ("external_id", "user", "title", "is_read")
    list_filter = ("is_read",)
    search_fields = ["user__email", "user__phone", "title"]  # Also searches by tags, as done in the overriden method
    readonly_fields = ("user",)


admin.site.register(PushNotificationHistory, PushNotificationHistoryAdmin)
