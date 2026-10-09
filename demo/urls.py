from django.contrib import admin
from django.urls import include, path

from api.health import live, ready

urlpatterns = [
    path("health/live/", live),
    path("health/ready/", ready),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]
