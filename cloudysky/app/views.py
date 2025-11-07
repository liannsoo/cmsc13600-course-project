from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
)
from datetime import datetime, time
from zoneinfo import ZoneInfo  # Python ≥ 3.9


# ====== HW4: index page (shows time + highlights current user) ======
def index(request):
    chicago = ZoneInfo("America/Chicago")
    now_cdt = datetime.now(tz=chicago)
    current_time = now_cdt.strftime("%H:%M")
    # Note: {{ user }} is available via context processors, but passing doesn't hurt
    return render(request, "app/index.html", {
        "current_time": current_time,
        "user": request.user,
    })


# ====== HW4: /app/new (GET only) ======
def new_user_form(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"], "This endpoint only accepts GET.")
    return render(request, "app/new.html")


# ====== HW4: /app/createUser (POST only) ======
@csrf_exempt
def create_user(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "Use POST when creating a user.")

    email = request.POST.get("email")
    username = request.POST.get("user_name")
    password = request.POST.get("password")
    last_name = request.POST.get("last_name", "")
    is_admin = request.POST.get("is_admin", "0") == "1"

    # Basic validation
    if not email or not username or not password:
        return HttpResponseBadRequest("Missing email, user_name, or password.")

    if User.objects.filter(email=email).exists():
        return HttpResponseBadRequest("A user with that email already exists.")
    if User.objects.filter(username=username).exists():
        return HttpResponseBadRequest("A user with that username already exists.")

    user = User.objects.create_user(username=username, password=password, email=email)
    if last_name:
        user.last_name = last_name
    if is_admin:
        user.is_staff = True
    user.save()

    login(request, user)
    return HttpResponse(f"User {username} successfully created and logged in!")


# ====== HW2/HW3 endpoints kept working ======
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
