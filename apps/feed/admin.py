from django.contrib import admin

from .models import (
    ClusterMap,
    Cluster
)

admin.site.register(ClusterMap)
admin.site.register(Cluster)
