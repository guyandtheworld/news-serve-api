from django.urls import path

from . import views

urlpatterns = [
    path("", views.Test.as_view(), name="index"),
    path("getuuid", views.GetUserUUID.as_view()),
    path("getclientuuid", views.GetClientUUID.as_view()),
    path("getclientname", views.GetClientName.as_view()),
    path("getuserstatus", views.GetClientName.as_view()),
    path("getuserdefaultscenario", views.GetUserDefaultScenario.as_view()),
]
