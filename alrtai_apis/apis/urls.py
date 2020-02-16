from django.urls import path

from . import views

urlpatterns = [
    path("", views.Test.as_view(), name="index"),
    path("getuuid", views.GetUserUUID.as_view()),
]
