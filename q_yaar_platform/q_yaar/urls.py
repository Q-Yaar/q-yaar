"""
URL configuration for q_yaar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from .forms import CustomAdminAuthenticationForm

admin.autodiscover()

admin.site.site_header = "Q Yaar Admin"
admin.site.site_title = "Q Yaar Admin"
admin.site.index_title = "Welcome to Q Yaar Admin Portal"
admin.site.enable_nav_sidebar = False
# To work with UUID based login
admin.site.login_form = CustomAdminAuthenticationForm

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("jwt_auth.api.urls")),
    path("api/v1/games/", include("game.api.urls")),
    path("api/v1/cards/", include("card_deck.api.urls")),
    path("api/v1/qna/", include("qna.api.urls")),
    path("api/v1/facts/", include("fact.api.urls")),
]
