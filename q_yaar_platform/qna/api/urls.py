from django.urls import path

from . import views

app_name = "qna"

urlpatterns = [
    # POST - Login
    path(r"rewards/", views.RewardsListView.as_view(), name="handler-rewards-list"),
    path(r"categories/", views.CategoriesListView.as_view(), name="handler-categories-list"),
    path(r"categories/<uuid:category_id>/questions/", views.QuestionListView.as_view(), name="handler-questions-list"),
    path(
        r"categories/<uuid:category_id>/questions/<uuid:question_id>",
        views.QuestionDetailView.as_view(),
        name="handler-questions-detail",
    ),
    path(r"game/<uuid:game_id>/questions", views.GameQuestionsListView.as_view(), name="handler-game-questions-list"),
    path(
        r"game/<uuid:game_id>/asked-questions",
        views.GameAskedQuestionsListView.as_view(),
        name="handler-game-asked-questions-list",
    ),
    path(
        r"game/<uuid:game_id>/questions/<uuid:question_id>/ask",
        views.GameQuestionsAskView.as_view(),
        name="handler-game-questions-ask",
    ),
    path(
        r"game/<uuid:game_id>/asked-questions/<uuid:asked_question_id>/answer",
        views.GameQuestionsAnswerView.as_view(),
        name="handler-game-questions-answer",
    ),
    path(
        r"game/<uuid:game_id>/asked-questions/<uuid:asked_question_id>/accept",
        views.GameQuestionsAnswerAcceptView.as_view(),
        name="handler-game-questions-answer-accept",
    ),
]
