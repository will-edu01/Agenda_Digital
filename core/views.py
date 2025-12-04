from datetime import datetime, timedelta, date
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Service, Appointment
from .utils.schedule import get_available_slots
#from .utils.send_email import send_appointment_confirmation



def home(request):
    today = date.today().isoformat()
    services = Service.objects.all().order_by('name')
    return render(request, "core/home.html", {
        "services": services,
        "today": date.today().isoformat()
    })


def get_available_times(request):
    date_str = request.GET.get("date")
    duration = int(request.GET.get("duration", 0))

    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    if date < datetime.today().date():
        return JsonResponse({"slots": []})

    slots = get_available_slots(date, duration)
    slots_str = [s.strftime("%H:%M") for s in slots]

    return JsonResponse({"slots": slots_str})


@require_POST
def confirm_api(request):

    service_ids = request.POST.getlist("services[]") or request.POST.getlist("services")
    selected_date = request.POST.get("selected_date")
    selected_time = request.POST.get("selected_time")

    if len(service_ids) == 1 and ',' in service_ids[0]:
        service_ids = service_ids[0].split(',')

    if not service_ids or not selected_date or not selected_time:
        return JsonResponse({"ok": False, "error": "Dados incompletos."}, status=400)

    try:
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
        time_obj = datetime.strptime(selected_time, "%H:%M").time()
    except ValueError:
        return JsonResponse({"ok": False, "error": "Formato de data/hora inválido."}, status=400)

    services = Service.objects.filter(id__in=service_ids)
    if not services.exists():
        return JsonResponse({"ok": False, "error": "Serviços não encontrados."}, status=404)

    total_minutes = sum(s.duration_minutes for s in services)
    total_price = sum(float(s.price) for s in services)

    start_dt = datetime.combine(date_obj, time_obj)
    end_dt = start_dt + timedelta(minutes=total_minutes)

    conflicts = Appointment.objects.filter(
        date=date_obj,
        start_time__lt=end_dt.time(),
        end_time__gt=time_obj
    )
    if conflicts.exists():
        return JsonResponse({"ok": False, "error": "Horário indisponível."}, status=409)

    if date_obj < date.today():
        return JsonResponse({"ok": False, "error": "Não é possível agendar em datas passadas."})

    services_json = [{"id": s.id, "name": s.name, "duration": s.duration_minutes, "price": float(s.price)} for s in services]

    return JsonResponse({
        "ok": True,
        "services": services_json,
        "total_minutes": total_minutes,
        "total_price": total_price,
        "selected_date": selected_date,
        "selected_time": selected_time,
        "_service_ids": service_ids
    })


@require_POST
def save_appointment_api(request):
    service_ids = request.POST.getlist("services[]")
    selected_date = request.POST.get("selected_date")
    selected_time = request.POST.get("selected_time")

    if not service_ids or not selected_date or not selected_time:
        return JsonResponse({"ok": False, "error": "Dados incompletos."}, status=400)

    try:
        start_dt = datetime.strptime(f"{selected_date} {selected_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return JsonResponse({"ok": False, "error": "Formato de data/hora inválido."}, status=400)

    services = Service.objects.filter(id__in=service_ids)
    if not services.exists():
        return JsonResponse({"ok": False, "error": "Serviços não encontrados."}, status=404)

    total_minutes = sum(s.duration_minutes for s in services)
    total_price = sum(float(s.price) for s in services)
    end_dt = start_dt + timedelta(minutes=total_minutes)

    conflicts = Appointment.objects.filter(
        date=start_dt.date(),
        start_time__lt=end_dt.time(),
        end_time__gt=start_dt.time()
    )
    if conflicts.exists():
        return JsonResponse({"ok": False, "error": "Horário já reservado."}, status=409)

    if start_dt.date() < date.today():
        return JsonResponse({"ok": False, "error": "Não é possível agendar em datas passadas."})

    ap = Appointment.objects.create(
        user=request.user,
        date=start_dt.date(),
        start_time=start_dt.time(),
        end_time=end_dt.time(),
        total_price=total_price,
        total_minutes=total_minutes
    )
    ap.services.set(services)

    """send_appointment_confirmation(
    request.user,
    services,
    selected_date,
    selected_time,
    total_price
    )"""

    return JsonResponse({"ok": True, "appointment_id": ap.id})


@login_required
def my_appointments_view(request):
    user = request.user

    appointments = Appointment.objects.filter(user=user).order_by("date", "start_time")

    upcoming = []
    past = []

    now = datetime.now()

    for ap in appointments:
        ap_datetime = datetime.combine(ap.date, ap.start_time)
        ap.services_list = ap.services.all()
        if ap_datetime >= now:
            upcoming.append(ap)
        else:
            past.append(ap)

    return render(request, "core/my_appointments.html", {
        "upcoming": upcoming,
        "past": past
    })
