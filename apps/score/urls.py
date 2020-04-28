from django.urls import path

from . import views

urlpatterns = [
    path("portfolio", views.GetPortfolioScore.as_view()),
    path("sentiment", views.GetSentiment.as_view()),
    path("newscount", views.GetNewsCount.as_view()),
    path("bucket", views.GetBucketScore.as_view()),
    path("entitybucket", views.GetEntityBucketScore.as_view())
]
