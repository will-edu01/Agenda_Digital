from django.urls import path
from .views_verification import register_step_one, register_verify_code
from .views import login_view, logout_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_step_one, name='register'),
    path('verify-email/', register_verify_code, name='verify_email'),
    path('logout/', logout_view, name='logout'),
]
