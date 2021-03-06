from django.urls import path

from . import views

urlpatterns = [
    path("portfolio", views.GetPortfolio.as_view()),
    path("entity", views.GetEntity.as_view()),
    path("bucket", views.GetBucket.as_view()),
    path("bucketentity", views.GetBucketEntity.as_view()),
    path("feedsearch", views.FeedSearch.as_view())
]
