from django.contrib import admin

from .models import Card, CardTag


class CardTagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]


admin.site.register(CardTag, CardTagAdmin)


class CardAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "reward")
    search_fields = ["title"]  # Also searches by tags, as done in the overriden method
    list_filter = ("tags",)
    filter_horizontal = ("tags",)

    # Override to use the base manager to include soft-deleted items
    def get_queryset(self, request):
        return self.model._base_manager.get_queryset()


admin.site.register(Card, CardAdmin)
