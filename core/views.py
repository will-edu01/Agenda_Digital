from datetime import datetime
from django.http import JsonResponse
from .utils.schedule import get_available_slots
from django.shortcuts import render, redirect
from .models import Service, Appointment


def home(request):
    services = Service.objects.all().order_by('name')
    return render(request, "core/home.html", {"services": services})


def select_datetime_view(request):
    if request.method != "POST":
        return redirect("home")

    # IDs dos serviços marcados
    service_ids = request.POST.getlist("services")

    if not service_ids:
        return redirect("home")

    # Buscar serviços no banco
    services = Service.objects.filter(id__in=service_ids)

    # Calcular totais
    total_minutes = sum((s.duration_minutes or 0) for s in services)
    total_price = sum((s.price or 0) for s in services)

    if total_minutes == 0:
        total_minutes = 1

    context = {
        "services": services,
        "total_price": total_price,
        "total_minutes": total_minutes,
        "service_ids": service_ids,
    }

    return render(request, "core/select_datetime.html", context)


def get_available_times(request):
    date_str = request.GET.get("date")
    duration = int(request.GET.get("duration"))

    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    slots = get_available_slots(date, duration)

    slots_str = [s.strftime("%H:%M") for s in slots]

    return JsonResponse({"slots": slots_str})


def confirm_appointment_view(request):
    if request.method != "POST":
        return redirect("home")

    selected_date = request.POST.get("selected_date")
    selected_time = request.POST.get("selected_time")
    service_ids = request.POST.getlist("services")

    if not (selected_date and selected_time and service_ids):
        return redirect("home")

    services = Service.objects.filter(id__in=service_ids)

    total_minutes = sum(s.duration_minutes for s in services)
    total_price = sum(s.price for s in services)

    context = {
        "services": services,
        "total_minutes": total_minutes,
        "total_price": total_price,
        "selected_date": selected_date,
        "selected_time": selected_time,
        "service_ids": service_ids,
    }

    return render(request, "core/confirm.html", context)


def save_appointment_view(request):
    if request.method != "POST":
        return redirect("home")

    selected_date = request.POST.get("selected_date")
    selected_time = request.POST.get("selected_time")
    service_ids = request.POST.getlist("services")

    services = Service.objects.filter(id__in=service_ids)

    total_minutes = sum(s.duration_minutes for s in services)
    total_price = sum(s.price for s in services)

    # calcular hora de término
    from datetime import datetime, timedelta
    start_dt = datetime.strptime(f"{selected_date} {selected_time}", "%Y-%m-%d %H:%M")
    end_dt = start_dt + timedelta(minutes=total_minutes)

    # criar agendamento
    ap = Appointment.objects.create(
        user=request.user,
        date=selected_date,
        start_time=selected_time,
        end_time=end_dt.time(),
        total_price=total_price,
        total_minutes=total_minutes,
    )
    ap.services.set(services)

    return render(request, "core/success.html", {"appointment": ap})
