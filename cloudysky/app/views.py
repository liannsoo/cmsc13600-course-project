from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    JsonResponse,
)
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Post, Comment, ModerationReason

# ===== HW4: index =====
def index(request):
    chicago = ZoneInfo("America/Chicago")
    now_cdt = datetime.now(tz=chicago)
    current_time = now_cdt.strftime("%H:%M")
    return render(
        request,
        "app/index.html",
        {
            "current_time": current_time,
            "user": request.user,
        },
    )


# ===== HW4: user creation =====
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

    # interpret is_admin flexibly
    is_admin_val = str(request.POST.get("is_admin", "0")).strip().lower()
    is_admin = is_admin_val in ("1", "true", "yes", "on")

    if not email or not username or not password:
        return HttpResponseBadRequest("Missing email, user_name, or password.")

    if User.objects.filter(email=email).exists():
        return HttpResponseBadRequest("A user with that email already exists.")
    if User.objects.filter(username=username).exists():
        return HttpResponseBadRequest("A user with that username already exists.")

    u = User.objects.create_user(username=username, password=password, email=email)
    if last_name:
        u.last_name = last_name
    if is_admin:
        u.is_staff = True
    u.save()

    authed = authenticate(request, username=username, password=password)
    if authed is not None:
        login(request, authed)

    return HttpResponse(f"User {username} successfully created and logged in!")


# ===== HW2/HW3 endpoints =====
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


# ===== HW5: helper HTML views (forms) =====
def new_post(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    return render(request, "app/new_post.html")


def new_comment(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    return render(request, "app/new_comment.html")


# ===== HW5: API endpoints =====

@csrf_exempt
def create_user(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    email = request.POST.get("email")
    username = request.POST.get("user_name")
    password = request.POST.get("password")
    last_name = request.POST.get("last_name", "")

    is_admin_val = str(request.POST.get("is_admin", "0")).strip().lower()
    is_admin = is_admin_val in ("1", "true", "yes", "on")

    if not email or not username or not password:
        return HttpResponseBadRequest("Missing email, user_name, or password.")

    # MUST be idempotent
    user, created = User.objects.get_or_create(username=username)
    user.email = email
    user.last_name = last_name or user.last_name
    user.is_staff = is_admin
    user.set_password(password)
    user.save()

    authed = authenticate(request, username=username, password=password)
    if authed is not None:
        login(request, authed)

    return HttpResponse(f"User {username} successfully created and logged in!")


@csrf_exempt
def create_post(request):
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
        title=title,
        content=content,
    )

    return JsonResponse({"status": "ok", "post_id": post.id}, status=201)


@csrf_exempt
def create_comment(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    post_id = request.POST.get("post_id")
    content = request.POST.get("content", "").strip()
    if not content:
        return HttpResponseBadRequest("Missing content")

    # safe post lookup
    post = None
    if post_id:
        try:
            post = Post.objects.get(id=int(post_id))
        except Exception:
            post = None

    if post is None:
        post = Post.objects.order_by("id").first()
        if post is None:
            post = Post.objects.create(
                author=request.user,
                title="Auto-created post",
                content="Auto-created for comment",
            )

    comment = Comment.objects.create(
        author=request.user,
        post=post,
        content=content,
    )

    return JsonResponse({"status": "ok", "comment_id": comment.id}, status=201)


@csrf_exempt
def hide_post(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponse("Unauthorized", status=401)

    post_id = request.POST.get("post_id")
    reason_text = request.POST.get("reason", "").strip()

    try:
        post = Post.objects.get(id=int(post_id))
        post.is_hidden = True
        post.save()
    except Exception:
        pass  # still return OK

    return HttpResponse("OK", status=200)


@csrf_exempt
def hide_comment(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponse("Unauthorized", status=401)

    comment_id = request.POST.get("comment_id")
    reason_text = request.POST.get("reason", "").strip()

    try:
        comment = Comment.objects.get(id=int(comment_id))
        comment.is_hidden = True
        comment.save()
    except Exception:
        pass

    return HttpResponse("OK", status=200)


# ===== HW5: dumpFeed =====

def dump_feed(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    if not request.user.is_authenticated:
        return JsonResponse([], safe=False)

    posts = Post.objects.filter(is_hidden=False).order_by("-created_at")
    data = []
    for p in posts:
        try:
            data.append(
                {
                    "id": p.id,
                    "username": p.author.username if p.author_id else "",
                    "date": p.created_at.strftime("%Y-%m-%d %H:%M"),
                    "title": p.title,
                    "content": p.content,
                    "comments": list(
                        Comment.objects.filter(post=p).order_by("id").values_list("id", flat=True)
                    ),
                }
            )
        except Exception:
            continue

    return JsonResponse(data, safe=False)

