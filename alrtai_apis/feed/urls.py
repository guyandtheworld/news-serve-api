from django.urls import path

from . import views

urlpatterns = [
    path("portfolio", views.GetPortfolio.as_view()),
]
