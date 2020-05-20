from django.urls import path

from . import views

urlpatterns = [
    path("listentities", views.ViewEntityType.as_view()),
    path("listalias", views.ListParentAlias.as_view()),
    path("changeparent", views.ChangeParentName.as_view()),
    path("mergeparents", views.MergeParents.as_view())
]
