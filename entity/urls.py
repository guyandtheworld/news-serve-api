from django.urls import path

from . import views

urlpatterns = [
    path("info", views.GetEntityInfo.as_view()),
    path("alias", views.GetEntityAlias.as_view()),
]
