from django.urls import path
from .views import (
    home,
    get_available_times,
    confirm_api,
    save_appointment_api,
    my_appointments_view,
)


urlpatterns = [
    path("", home, name="home"),
    path('horarios/', get_available_times, name='available_times'),
    path("api/confirm/", confirm_api, name="confirm_api"),
    path("api/save/", save_appointment_api, name="save_appointment_api"),
    path("minha-agenda/", my_appointments_view, name="my_appointments"),
]
