from django.urls import path

from . import views

urlpatterns = [
    path("listentities", views.ViewEntityType.as_view())
]
