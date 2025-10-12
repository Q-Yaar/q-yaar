from django.contrib import admin

from .models import Card


class CardAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "reward")
    search_fields = ["title"]  # Also searches by tags, as done in the overriden method

    # Override to use the base manager to include soft-deleted items
    def get_queryset(self, request):
        return self.model._base_manager.get_queryset()
    
    def get_search_results(self, request, queryset, search_term):
        # Start with normal search (title, etc.)
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        # Add tag search — case-insensitive match for any tag containing the search term
        tag_matches = self.model._base_manager.filter(tags__icontains=search_term)

        # Combine the two querysets
        queryset = queryset | tag_matches
        return queryset, use_distinct


admin.site.register(Card, CardAdmin)
