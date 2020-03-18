from django.urls import path

from . import views

urlpatterns = [
    path("info", views.EntityInfo.as_view()),
    path("alias", views.EntityAlias.as_view()),
    path("portfolio", views.ListPortfolio.as_view()),
    path("listscenarioentities", views.ListScenarioEntities.as_view()),
    path("addentity", views.AddEntity.as_view()),
    path("addalias", views.AddAlias.as_view()),
    path("addtoportfolio", views.AddToPortfolio.as_view())
]