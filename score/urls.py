from django.urls import path

from . import views

urlpatterns = [
    path("portfolio", views.GetPortfolioScore.as_view()),
]
