from django.contrib import admin

from .models import GeoImport


@admin.register(GeoImport)
class GeoImportAdmin(admin.ModelAdmin):
    list_display = ("source", "started", "finished", "feature_count", "status")
    list_filter = ("status",)
    search_fields = ("source",)
