from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("apps/", include("Apps.urls")),
    path("admin/", admin.site.urls),
]