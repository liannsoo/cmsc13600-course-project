from django.urls import path
from . import views

urlpatterns = [
    # index under /app/ and /app/index.html
    path("", views.index, name="app_index"),
    path("index.html", views.index, name="app_index_html"),

    # HW4 user creation
    path("new/", views.new_user_form),
    path("createUser/", views.create_user),  # autograder uses this

    # HW5 helper HTML forms (not graded but useful)
    path("new_post/", views.new_post),
    path("new_comment/", views.new_comment),

    # HW5 API endpoints
    path("createPost/", views.create_post),
    path("createComment/", views.create_comment),
    path("hidePost/", views.hide_post),
    path("hideComment/", views.hide_comment),
    path("dumpFeed/", views.dump_feed),
]

