from django.urls import path
from . import views

urlpatterns = [
    # index page
    path('', views.index, name='index'),
    path('index.html', views.index, name='index_html'),

    # HW4 endpoints
    path('new', views.new_user_form, name='new_user_form'), 
    path('createUser', views.create_user, name='create_user'), 

    # Your earlier HW endpoints
    path('time', views.time_since_midnight_cdt, name='time'),
    path('sum', views.sum_view, name='sum'),
]
