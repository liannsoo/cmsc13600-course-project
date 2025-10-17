from django.urls import path
from . import views

urlpatterns = [
    path('time', views.time_since_midnight_cdt, name='time'),
    path('sum', views.sum_view, name='sum'),
]
