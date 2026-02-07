from django.contrib import admin

from .models import Fact


class FactAdmin(admin.ModelAdmin):
    list_display = ("game", "target_team", "fact_type", "created", "modified")
    search_fields = ["external_id", "game__game_code", "target_team__team_name"]
    list_filter = ("fact_type",)

    # Override to use the base manager to include soft-deleted items
    def get_queryset(self, request):
        return self.model._base_manager.get_queryset()


admin.site.register(Fact, FactAdmin)
