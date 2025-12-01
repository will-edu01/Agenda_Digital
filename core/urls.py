from django.urls import path
from .views import (
    home,
    get_available_times,
    select_datetime_view,
    confirm_api,
    save_appointment_api,
)


urlpatterns = [
    path("", home, name="home"),
    path('horarios/', get_available_times, name='available_times'),
    path("selecionar-horario/", select_datetime_view, name="select_datetime"),
    path("api/confirm/", confirm_api, name="confirm_api"),
    path("api/save/", save_appointment_api, name="save_appointment_api"),
]
