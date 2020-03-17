from django.urls import path

from . import views

urlpatterns = [
    path("info", views.AddEntityInfo.as_view()),
    path("alias", views.AddEntityAlias.as_view()),
    path("portfolio", views.ListPortfolio.as_view())
]
