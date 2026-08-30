from django.contrib import admin

from .models import (
    AskedQuestion,
    GameQuestion,
    QuestionCategory,
    QuestionReward,
    QuestionTemplate,
)


class QuestionRewardAdmin(admin.ModelAdmin):
    list_display = ("reward_name", "reward_type")
    search_fields = ["reward_name"]
    list_filter = ("reward_type",)

    # Override to use the base manager to include soft-deleted items
    def get_queryset(self, request):
        return self.model._base_manager.get_queryset()


admin.site.register(QuestionReward, QuestionRewardAdmin)


class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ("category_name", "reward", "priority")
    search_fields = ["category_name", "reward__reward_name"]
    list_filter = ("reward__reward_type",)

    # Override to use the base manager to include soft-deleted items
    def get_queryset(self, request):
        return self.model._base_manager.get_queryset()


admin.site.register(QuestionCategory, QuestionCategoryAdmin)


class QuestionTemplateAdmin(admin.ModelAdmin):
    list_display = ("external_id", "category")
    search_fields = ["external_id", "category__category_name"]
    list_filter = ("category__reward__reward_type",)

    # Override to use the base manager to include soft-deleted items
    def get_queryset(self, request):
        return self.model._base_manager.get_queryset()


admin.site.register(QuestionTemplate, QuestionTemplateAdmin)


class GameQuestionAdmin(admin.ModelAdmin):
    list_display = ("question_template", "game")
    search_fields = [
        "question_template__external_id",
        "question_template__category__category_name",
        "game__game_code",
        "game__name",
    ]
    readonly_fields = ("question_template", "game")


admin.site.register(GameQuestion, GameQuestionAdmin)


class AskedQuestionAdmin(admin.ModelAdmin):
    list_display = ("game_question", "target")
    search_fields = [
        "game_question__question_template__external_id",
        "game_question__game__game_code",
        "game_question__game__name",
        "target__team_name",
    ]
    readonly_fields = ("game_question", "target")


admin.site.register(AskedQuestion, AskedQuestionAdmin)
