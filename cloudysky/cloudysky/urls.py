from django.contrib import admin
from django.urls import path, include
from app import views  # so we can point root ('/') at index

urlpatterns = [
    path('admin/', admin.site.urls),

    # Root index paths the autograder expects:
    path('', views.index, name='home'),          # GET /
    path('index.html', views.index, name='home_html'),  # GET /index.html

    # Your app endpoints, including /app/new and /app/createUser:
    path('app/', include('app.urls')),

    # Django built-in auth (for /accounts/login/)
    path('accounts/', include('django.contrib.auth.urls')),
]

