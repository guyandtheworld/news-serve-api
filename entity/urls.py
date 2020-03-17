from django.urls import path

from . import views

urlpatterns = [
    path("info", views.AddEntityInfo.as_view()),
    path("alias", views.AddEntityAlias.as_view()),
    path("portfolio", views.ListPortfolio.as_view()),
    path("listscenarioentities", views.ListScenarioEntities.as_view()),
    path("addentity", views.AddEntity.as_view()),
    path("addalias", views.AddAlias.as_view())
]
