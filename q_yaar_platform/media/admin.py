from django.contrib import admin

from .models import Asset


class AssetAdmin(admin.ModelAdmin):
    list_display = ("external_id", "status", "asset_name")
    search_fields = ["external_id", "object_key", "asset_name"]
    list_filter = ("status",)
    readonly_fields = ("external_id", "object_key", "uploaded_by", "created", "modified")


admin.site.register(Asset, AssetAdmin)
