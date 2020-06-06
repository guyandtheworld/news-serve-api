from django.urls import path

from . import views

urlpatterns = [
    path("unverifiedentities", views.ListVerifiableEntities.as_view()),
    path("updateentities", views.UpdateEntities.as_view()),
    path("verifyentity", views.VerifyEntity.as_view()),
    path("unverifiedscenarios", views.UnverifiedScenarios.as_view()),
    path("updatebucket", views.UpdateBucket.as_view()),
    path("scenariostatus", views.ChangeScenarioStatus.as_view())

]
