from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("apiauth", obtain_auth_token),
    path("getuuid", views.GetUserUUID.as_view()),
    path("getclientuuid", views.GetClientUUID.as_view()),
    path("getclientname", views.GetClientName.as_view()),
    path("getuserstatus", views.GetClientName.as_view()),
    path("getuserdefaultscenario", views.GetUserDefaultScenario.as_view()),
    path("getscenarioname", views.GetScenarioName.as_view()),
    path("getbuckets", views.GetBuckets.as_view()),
    path("getbucketweights", views.GetBucketWeights.as_view()),
    path("addentity", views.AddEntity.as_view()),
    path("addalias", views.AddAlias.as_view()),
    path("logout", views.Logout.as_view()),
    path("signup", views.SignUp.as_view()),
]
