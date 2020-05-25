from django.contrib import admin

from .models import (
    StoryWarehouse,
    ClusterMap,
    Cluster
)

admin.site.register(StoryWarehouse)
admin.site.register(ClusterMap)
admin.site.register(Cluster)
