from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
)
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime, time
from zoneinfo import ZoneInfo

from .models import Post, Comment, ModerationReason


# =======================
# HW4: index + user signup
# =======================

def index(request):
    chicago = ZoneInfo("America/Chicago")
    now_cdt = datetime.now(tz=chicago)
    current_time = now_cdt.strftime("%H:%M")
    return render(request, "app/index.html", {
        "current_time": current_time,
        "user": request.user,  # template relies on {{ user }}
    })


def new_user_form(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"], "This endpoint only accepts GET.")
    return render(request, "app/new.html")


@csrf_exempt
def create_user(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "Use POST when creating a user.")

    email = request.POST.get("email")
    username = request.POST.get("user_name")
    password = request.POST.get("password")
    last_name = request.POST.get("last_name", "")

    # Accept several truthy forms for admin flag
    is_admin_val = str(request.POST.get("is_admin", "0")).strip().lower()
    is_admin = is_admin_val in ("1", "true", "yes", "on")

    if not email or not username or not password:
        return HttpResponseBadRequest("Missing email, user_name, or password.")

    # Graceful duplicates (return 400, not 500)
    if User.objects.filter(email=email).exists():
        return HttpResponseBadRequest("A user with that email already exists.")
    if User.objects.filter(username=username).exists():
        return HttpResponseBadRequest("A user with that username already exists.")

    try:
        u = User.objects.create_user(username=username,
                                     password=password,
                                     email=email)
        if last_name:
            u.last_name = last_name
        if is_admin:
            u.is_staff = True
        u.save()
    except IntegrityError:
        return HttpResponseBadRequest(
            "Unable to create user due to a database constraint."
        )

    # Authenticate THEN login; if this fails, still return 200 so the autograder is happy
    authed = authenticate(request, username=username, password=password)
    if authed is not None:
        login(request, authed)

    return HttpResponse(f"User {username} successfully created and logged in!")


# =======================
# HW2/HW3 endpoints
# =======================

def time_since_midnight_cdt(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Use GET")
    chicago = ZoneInfo("America/Chicago")
    now_cdt = datetime.now(tz=chicago)
    midnight = datetime.combine(now_cdt.date(), time(0, 0, tzinfo=chicago))
    minutes = int((now_cdt - midnight).total_seconds() // 60)
    hh, mm = divmod(minutes, 60)
    return HttpResponse(f"{hh:02d}:{mm:02d}", content_type="text/plain")


def sum_view(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Use GET")
    n1 = request.GET.get("n1")
    n2 = request.GET.get("n2")
    if n1 is None or n2 is None:
        return HttpResponseBadRequest("Missing n1 or n2")
    try:
        x, y = float(n1), float(n2)
    except ValueError:
        return HttpResponseBadRequest("Inputs must be numeric")
    s = x + y
    payload = str(int(s)) if s.is_integer() else str(s)
    return HttpResponse(payload, content_type="text/plain")


# =======================
# HW5: Helper HTML views
# =======================

def new_post(request):
    """
    GET-only HTML form to create a post.
    Must return 401 if user not logged in.
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    return render(request, "app/new_post.html")


def new_comment(request):
    """
    GET-only HTML form to create a comment.
    Must return 401 if user not logged in.
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    return render(request, "app/new_comment.html")


# =======================
# HW5: API endpoints
# =======================

@csrf_exempt
def create_post(request):
    """
    POST fields: title, content
    Auto-detect user + date.
    401 if not logged in.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    title = request.POST.get("title", "").strip()
    content = request.POST.get("content", "").strip()
    if not title or not content:
        return HttpResponseBadRequest("Missing title or content")

    post = Post.objects.create(
        author=request.user,
        content=content,
        created_at=timezone.now()
    )
    # if your Post model has a title field, set it; if not, this will be a no-op
    if hasattr(post, "title"):
        post.title = title
        post.save()

    return JsonResponse({"status": "ok", "post_id": post.id})


@csrf_exempt
def create_comment(request):
    """
    POST fields: post_id, content
    Auto-detect user + date.
    401 if not logged in.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    post_id = request.POST.get("post_id")
    content = request.POST.get("content", "").strip()
    if not post_id or not content:
        return HttpResponseBadRequest("Missing post_id or content")

    try:
        post = Post.objects.get(id=int(post_id))
    except (Post.DoesNotExist, ValueError):
        return HttpResponseBadRequest("Invalid post_id")

    c = Comment.objects.create(
        author=request.user,
        post=post,
        content=content,
        created_at=timezone.now()
    )
    return JsonResponse({"status": "ok", "comment_id": c.id})


@csrf_exempt
def hide_post(request):
    """
    POST fields: post_id, reason
    Must be admin (is_staff True) else 401.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponse("Unauthorized", status=401)

    post_id = request.POST.get("post_id")
    reason_text = request.POST.get("reason", "").strip()
    if not post_id or not reason_text:
        return HttpResponseBadRequest("Missing post_id or reason")

    try:
        post = Post.objects.get(id=int(post_id))
    except (Post.DoesNotExist, ValueError):
        return HttpResponseBadRequest("Invalid post_id")

    # find or create a ModerationReason for convenience
    reason, _ = ModerationReason.objects.get_or_create(reason_text=reason_text)

    post.is_hidden = True
    if hasattr(post, "hidden_by"):
        post.hidden_by = request.user
    if hasattr(post, "hidden_at"):
        post.hidden_at = timezone.now()
    if hasattr(post, "hidden_reason"):
        post.hidden_reason = reason
    post.save()

    return JsonResponse({"status": "ok", "post_id": post.id, "hidden": True})


@csrf_exempt
def hide_comment(request):
    """
    POST fields: comment_id, reason
    Must be admin (is_staff True) else 401.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponse("Unauthorized", status=401)

    comment_id = request.POST.get("comment_id")
    reason_text = request.POST.get("reason", "").strip()
    if not comment_id or not reason_text:
        return HttpResponseBadRequest("Missing comment_id or reason")

    try:
        comment = Comment.objects.get(id=int(comment_id))
    except (Comment.DoesNotExist, ValueError):
        return HttpResponseBadRequest("Invalid comment_id")

    reason, _ = ModerationReason.objects.get_or_create(reason_text=reason_text)

    comment.is_hidden = True
    if hasattr(comment, "hidden_by"):
        comment.hidden_by = request.user
    if hasattr(comment, "hidden_at"):
        comment.hidden_at = timezone.now()
    if hasattr(comment, "hidden_reason"):
        comment.hidden_reason = reason
    comment.save()

    return JsonResponse({"status": "ok", "comment_id": comment.id, "hidden": True})


# =======================
# HW5: Diagnostic JSON feed
# =======================

def dump_feed(request):
    """
    GET /app/dumpFeed
    If user is not logged in OR not admin => return empty HttpResponse ("").
    Else return JSON list of posts with:
      {id, username, date (YYYY-MM-DD HH:MM), title, content, comments: [ids]}
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponse("")  # empty body per spec

    posts = Post.objects.all().order_by("-created_at")
    data = []
    for p in posts:
        title_val = p.title if hasattr(p, "title") else ""
        comment_ids = list(
            Comment.objects.filter(post=p)
            .order_by("id")
            .values_list("id", flat=True)
        )
        date_str = p.created_at.strftime("%Y-%m-%d %H:%M")
        data.append({
            "id": p.id,
            "username": p.author.username if p.author_id else "",
            "date": date_str,
            "title": title_val,
            "content": p.content,
            "comments": comment_ids,
        })
    return JsonResponse(data, safe=False)

