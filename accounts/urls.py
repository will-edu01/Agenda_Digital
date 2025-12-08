from django.urls import path
from django.contrib.auth import views as auth_views
from .views_profile import profile, update_profile
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
    path('profile/', profile, name='profile'),
    path('profile/update/', update_profile, name='update_profile'),

    path('password/change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
]
