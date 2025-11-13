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
    # HW5: HTML helper forms
    path('new_post', views.new_post, name='new_post'),
    path('new_comment', views.new_comment, name='new_comment'),

    # HW5: API endpoints
    path('createPost', views.create_post, name='create_post'),
    path('createComment', views.create_comment, name='create_comment'),
    path('hidePost', views.hide_post, name='hide_post'),
    path('hideComment', views.hide_comment, name='hide_comment'),

    # HW5: Diagnostic
    path('dumpFeed', views.dump_feed, name='dump_feed'),
]

