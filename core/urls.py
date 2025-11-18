from django.urls import path
from .views import home, select_datetime_view, get_available_times, confirm_appointment_view

urlpatterns = [
    path("", home, name="home"),
    path("selecionar-horario/", select_datetime_view, name="select_datetime"),
    path('horarios/', get_available_times, name='available_times'),
    path("confirmar/", confirm_appointment_view, name="confirm"),
]
