from django.urls import path
from .views import login_view, logout_view
from .views_verification import (
    register_step_one,
    register_verify_code,
    resend_verification_code,
)


urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_step_one, name='register'),
    path('verify-email/', register_verify_code, name='verify_email'),
    path('logout/', logout_view, name='logout'),
    path('resend-code/', resend_verification_code, name='resend_code'),
]
