from django.contrib import admin

from .models import (
    PortfolioWarehouse,
    AutoWarehouse,
    ClusterMap,
    Cluster
)

admin.site.register(PortfolioWarehouse)
admin.site.register(AutoWarehouse)
admin.site.register(ClusterMap)
admin.site.register(Cluster)
