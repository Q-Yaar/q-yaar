from django.contrib import admin

from .models import Card, CardInstance, CardTag


class CardTagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]


admin.site.register(CardTag, CardTagAdmin)


class CardAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "card_type", "reward")
    search_fields = ["title"]
    list_filter = ("tags", "card_type")
    filter_horizontal = ("tags",)

    # Override to use the base manager to include soft-deleted items
    def get_queryset(self, request):
        return self.model._base_manager.get_queryset()


admin.site.register(Card, CardAdmin)


class CardInstanceAdmin(admin.ModelAdmin):
    list_display = ("card", "team", "pile")
    search_fields = ["card__title", "team__team_name"]
    readonly_fields = ("card", "team")


admin.site.register(CardInstance, CardInstanceAdmin)
