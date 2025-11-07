from django.urls import path
from . import views

urlpatterns = [
    # index inside /app/ (not required, but fine to keep)
    path('', views.index, name='app_index'),

    # HW4 endpoints
    path('new', views.new_user_form, name='new_user_form'),
    path('createUser', views.create_user, name='create_user'),

    # HW2/HW3
    path('time', views.time_since_midnight_cdt, name='time'),
    path('sum', views.sum_view, name='sum'),
]
