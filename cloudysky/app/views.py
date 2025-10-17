from django.http import HttpResponse, HttpResponseBadRequest
from datetime import datetime, time
from zoneinfo import ZoneInfo  # Python ≥3.9

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

