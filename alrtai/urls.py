from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="alrt.ai API",
        default_version='v1',
        description="APIs for alrt.ai",
        contact=openapi.Contact(email="adarsh@alrt.ai"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # path("", schema_view.with_ui('swagger', cache_timeout=0)),
    path("admin/", admin.site.urls),
    path("api/v1/user/", include("apis.urls")),
    path("api/v1/feed/", include("feed.urls")),
    path("api/v1/score/", include("score.urls")),
    path("api/v1/entity/", include("entity.urls")),
    path("api/v1/viz/", include("viz.urls")),
    path("api/v1/auto/", include("auto.urls")),
    path("api/v1/dash/", include("admindash.urls"))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
