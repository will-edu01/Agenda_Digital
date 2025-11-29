from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm, RegisterForm
from accounts.models import User


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        
        if form.is_valid():
            user = form.cleaned_data["user"]
            remember_me = form.cleaned_data.get("remember_me")

            login(request, user)

            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)

            return redirect("home")
        
        for error in form.non_field_errors():
            messages.error(request, error)

    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})



def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]
            password = form.cleaned_data["password"]

            user = User.objects.create_user(
                email=email,
                password=password,
                name=name,
                phone=phone
            )

            messages.success(request, "Cadastro realizado com sucesso! Faça login para continuar.")
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})



def logout_view(request):
    logout(request)
    return redirect('login')
