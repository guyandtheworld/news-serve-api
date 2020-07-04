from django.urls import path

from . import views

urlpatterns = [
    path("listentities", views.ViewEntityType.as_view()),
    path("listalias", views.ListParentAlias.as_view()),
    path("change", views.ChangeParentName.as_view()),
    path("merge", views.MergeParents.as_view()),
    path("scenarioentity", views.ScenarioEntityType.as_view())
]
