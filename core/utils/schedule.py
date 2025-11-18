from datetime import datetime, timedelta, time
from core.models import WorkDay, BreakPeriod, SpecialDay, Appointment

def time_range(start, end, step_minutes):
    """Gera uma lista de horários entre start e end."""
    current = start
    delta = timedelta(minutes=step_minutes)
    while current + delta <= end:
        yield current
        current += delta

def overlaps(start1, end1, start2, end2):
    """Verifica se dois períodos se sobrepõem."""
    return max(start1, start2) < min(end1, end2)

def get_available_slots(date, service_duration):
    """
    Retorna uma lista de horários disponíveis (datetime.time).
    service_duration é o total em minutos.
    """
    weekday = date.weekday()

    # 1. SPECIAL DAY?
    try:
        special = SpecialDay.objects.get(date=date)
        if special.is_closed:
            return []  # fechado
        work_start = special.start_time
        work_end = special.end_time
        breaks = []
    except SpecialDay.DoesNotExist:
        # 2. USAR O EXPEDIENTE PADRÃO (WorkDay)
        try:
            wd = WorkDay.objects.get(weekday=weekday)
            work_start = wd.start_time
            work_end = wd.end_time
            breaks = list(wd.breaks.all())
        except WorkDay.DoesNotExist:
            return []  # não atende neste dia

    # 3. Agendamentos já existentes
    existing = Appointment.objects.filter(date=date)

    available = []

    # 4. Gerar horários possíveis usando intervalos fixos de 5 minutos (exato)
    for slot in time_range(
        datetime.combine(date, work_start),
        datetime.combine(date, work_end),
        5
    ):
        start = slot.time()
        end_dt = slot + timedelta(minutes=service_duration)
        end = end_dt.time()

        if end > work_end:
            continue

        # 5. Checar conflito com intervalos
        conflict = False
        for br in breaks:
            if overlaps(start, end, br.start_time, br.end_time):
                conflict = True
                break
        if conflict:
            continue

        # 6. Checar conflito com agendamentos existentes
        for ap in existing:
            if overlaps(start, end, ap.start_time, ap.end_time):
                conflict = True
                break
        if conflict:
            continue

        available.append(start)

    return available
