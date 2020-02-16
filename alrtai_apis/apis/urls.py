from django.urls import path

from . import views

urlpatterns = [
    path("getuuid", views.GetUserUUID.as_view()),
    path("getclientuuid", views.GetClientUUID.as_view()),
    path("getclientname", views.GetClientName.as_view()),
    path("getuserstatus", views.GetClientName.as_view()),
    path("getuserdefaultscenario", views.GetUserDefaultScenario.as_view()),
    path("getscenarioname", views.GetScenarioName.as_view()),
    path("getbuckets", views.GetBuckets.as_view()),
    path("getbucketweights", views.GetBucketWeights.as_view()),
]
