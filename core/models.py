from django.db import models
from django.conf import settings

class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(help_text="Duração em minutos")

    def __str__(self):
        return f"{self.name} - R${self.price}"

class WorkDay(models.Model):
    DAYS_OF_WEEK = [
        (0, "Segunda"),
        (1, "Terça"),
        (2, "Quarta"),
        (3, "Quinta"),
        (4, "Sexta"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    weekday = models.IntegerField(choices=DAYS_OF_WEEK, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_weekday_display()} — {self.start_time} às {self.end_time}"


class BreakPeriod(models.Model):
    workday = models.ForeignKey(WorkDay, on_delete=models.CASCADE, related_name="breaks")
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"Intervalo {self.start_time} às {self.end_time} ({self.workday.get_weekday_display()})"


class SpecialDay(models.Model):
    date = models.DateField(unique=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        if self.is_closed:
            return f"{self.date} — Fechado"
        return f"{self.date} — {self.start_time} às {self.end_time}"
    
class Appointment(models.Model):
    status = models.CharField(
    max_length=20,
    choices=[("scheduled", "Agendado"), ("canceled", "Cancelado")],
    default="scheduled"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_minutes = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} — {self.date} {self.start_time}"