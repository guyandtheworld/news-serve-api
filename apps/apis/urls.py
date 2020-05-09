from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("addbuckets", views.AddBuckets.as_view()),
    path("addkeywords", views.AddKeywords.as_view()),
    path("addscenario", views.CreateScenario.as_view()),
    path("apiauth", views.ObtainCustomAuthToken.as_view()),
    path("getuuid", views.GetUserUUID.as_view()),
    path("getclientuuid", views.GetClientUUID.as_view()),
    path("getclientname", views.GetClientName.as_view()),
    path("getuserstatus", views.GetUserStatus.as_view()),
    path("getuserdefaultscenario", views.GetUserDefaultScenario.as_view()),
    path("getscenarioname", views.GetScenarioName.as_view()),
    path("getbuckets", views.GetBuckets.as_view()),
    path("getbucketweights", views.GetBucketWeights.as_view()),
    path("listallscenario", views.ListAllScenario.as_view()),
    path("listallclients", views.ListAllClients.as_view()),
    path("listuserscenario", views.ListUserScenario.as_view()),
    path("listscenariodetails", views.ListScenarioDetails.as_view()),
    path("logout", views.Logout.as_view()),
    path("signup", views.SignUp.as_view()),
    path("subscribescenario", views.SubscribeScenario.as_view()),

    # To add custom forgot password page add template_name = "path to html" as argument to as_view()
    path("reset_password", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("reset_password_sent", auth_views.PasswordResetDoneView.as_view(),
         name="password_reset_done"),
    path("reset/<uidb64>/<token>", auth_views.PasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
    path("reset_password_complete", auth_views.PasswordResetCompleteView.as_view(),
         name="password_reset_complete"),
]
