from django.contrib import admin
from .models import Service, WorkDay, BreakPeriod, SpecialDay, Appointment


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_minutes')
    search_fields = ('name',)
    
@admin.register(WorkDay)
class WorkDayAdmin(admin.ModelAdmin):
    list_display = ("weekday", "start_time", "end_time")

@admin.register(BreakPeriod)
class BreakPeriodAdmin(admin.ModelAdmin):
    list_display = ("workday", "start_time", "end_time")

@admin.register(SpecialDay)
class SpecialDayAdmin(admin.ModelAdmin):
    list_display = ("date", "start_time", "end_time", "is_closed")

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "start_time", "end_time", "total_price", "status")
    list_filter = ("date", "status")
    search_fields = ("user__email", "user__name")