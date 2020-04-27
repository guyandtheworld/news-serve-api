from django.urls import path

from . import views


urlpatterns = [
    path("newscount", views.NewsCountViz.as_view()),
    path("sentiment", views.SentimentViz.as_view()),
    path("bucketscore", views.BucketScoreViz.as_view()),
    path("globedata", views.GetGlobeData.as_view())
]
