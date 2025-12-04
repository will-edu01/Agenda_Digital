from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .models import Service, Appointment
from .utils.schedule import get_available_slots



def home(request):
    services = Service.objects.all().order_by('name')
    return render(request, "core/home.html", {"services": services})


def get_available_times(request):
    date_str = request.GET.get("date")
    duration = int(request.GET.get("duration", 0))
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    slots = get_available_slots(date, duration)
    slots_str = [s.strftime("%H:%M") for s in slots]
    return JsonResponse({"slots": slots_str})


def select_datetime_view(request):
    if request.method != "POST":
        return redirect("home")

    service_ids = request.POST.getlist("services")
    if not service_ids:
        services_raw = request.POST.get("services")
        if services_raw:
            import re
            service_ids = re.split(r"[\s,]+", services_raw.strip())
            service_ids = [s for s in service_ids if s]

    if not service_ids:
        return redirect("home")

    try:
        ids_int = [int(x) for x in service_ids]
    except Exception:
        ids_int = []
        for s in service_ids:
            try:
                ids_int.append(int(s))
            except Exception:
                continue

    if not ids_int:
        return redirect("home")

    services_qs = Service.objects.filter(id__in=ids_int)

    if not services_qs.exists():
        return redirect("home")

    total_minutes = sum((s.duration_minutes or 0) for s in services_qs)
    total_price = sum((s.price or 0) for s in services_qs)
    if total_minutes == 0:
        total_minutes = 1

    selected_services = [str(s.id) for s in services_qs]

    context = {
        "services": services_qs,
        "total_minutes": total_minutes,
        "total_price": total_price,
        "selected_services": selected_services,
    }

    return render(request, "core/select_datetime.html", context)


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

    ap = Appointment.objects.create(
        user=request.user,
        date=start_dt.date(),
        start_time=start_dt.time(),
        end_time=end_dt.time(),
        total_price=total_price,
        total_minutes=total_minutes
    )
    ap.services.set(services)

    return JsonResponse({"ok": True, "appointment_id": ap.id})


#caso seja necessario adicionar a view de seleção de data/hora nas urls novamente:
#select_datetime_view,
#path("selecionar-horario/", select_datetime_view, name="select_datetime"),