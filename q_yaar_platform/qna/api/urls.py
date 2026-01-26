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
]
