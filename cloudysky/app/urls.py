from django.urls import path
from . import views

urlpatterns = [
    # Optional: /app/ can also show the same index page
    path('', views.index, name='app_index'),
    path('new', views.new_user_form, name='new_user_form'),
    path('createUser', views.create_user, name='create_user'),

    # earlier HW endpoints
    path('time', views.time_since_midnight_cdt, name='time'),
    path('sum', views.sum_view, name='sum'),
]

