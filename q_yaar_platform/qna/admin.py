from django.contrib import admin

from .models import (
    AskedQuestion,
    GameQuestion,
    Placeholder,
    PlaceholderAllowedValue,
    QuestionCategory,
    QuestionReward,
    QuestionTemplate,
)


class QuestionRewardAdmin(admin.ModelAdmin):
    list_display = ("reward_name", "reward_type")
    search_fields = ["reward_name"]
    list_filter = ("reward_type",)


admin.site.register(QuestionReward, QuestionRewardAdmin)


class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ("category_name", "reward", "priority")
    search_fields = ["category_name", "reward__reward_name"]
    list_filter = ("reward__reward_type",)


admin.site.register(QuestionCategory, QuestionCategoryAdmin)


class QuestionTemplateAdmin(admin.ModelAdmin):
    list_display = ("external_id", "category")
    search_fields = ["external_id", "category__category_name"]
    list_filter = ("category__reward__reward_type",)


admin.site.register(QuestionTemplate, QuestionTemplateAdmin)


class PlaceholderAdmin(admin.ModelAdmin):
    list_display = ("question", "placeholder_name", "required")
    search_fields = ["question__external_id", "placeholder_name"]
    list_filter = ("required",)


admin.site.register(Placeholder, PlaceholderAdmin)


class PlaceholderAllowedValueAdmin(admin.ModelAdmin):
    list_display = ("placeholder", "value")
    search_fields = ["placeholder__placeholder_name", "value"]


admin.site.register(PlaceholderAllowedValue, PlaceholderAllowedValueAdmin)


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
