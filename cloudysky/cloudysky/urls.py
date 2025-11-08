from django.contrib import admin
from django.urls import path, include
from app import views as app_views

urlpatterns = [
    path("", app_views.index, name="root_index"),
    path("index.html", app_views.index, name="index_html"),
    path("app/", include("app.urls")),
    # Include all default auth routes: /accounts/login/, /accounts/logout/, etc.
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
]

