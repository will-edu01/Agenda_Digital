import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

from .models_verification import VerificationCode
from accounts.models import User
from .forms import RegisterForm


def register_step_one(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            # Dados válidos → gerar código
            email = form.cleaned_data["email"]

            # Verifica se já existe usuário
            if User.objects.filter(email=email).exists():
                messages.error(request, "Já existe uma conta com este e-mail.")
                return redirect("register")

            # Gera código aleatório de 6 dígitos
            code = f"{random.randint(100000, 999999)}"

            # Salva temporariamente
            VerificationCode.objects.create(email=email, code=code)

            # Salva dados do formulário na sessão
            request.session["register_data"] = form.cleaned_data

            # Envia e-mail
            send_mail(
                "Seu código de verificação",
                f"Seu código é: {code}",
                settings.EMAIL_HOST_USER,
                [email],
            )

            # Redireciona para etapa 2
            return redirect("register_verify")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def register_verify_code(request):
    if "register_data" not in request.session:
        messages.error(request, "Sua sessão expirou. Preencha o cadastro novamente.")
        return redirect("register")

    email = request.session["register_data"]["email"]

    if request.method == "POST":
        user_code = request.POST.get("code")

        try:
            entry = VerificationCode.objects.filter(email=email).latest("created_at")
        except VerificationCode.DoesNotExist:
            messages.error(request, "Código não encontrado. Tente novamente.")
            return redirect("register")

        # Verifica expiração (10 minutos)
        if entry.created_at < timezone.now() - timedelta(minutes=10):
            messages.error(request, "Código expirado. Solicite outro.")
            return redirect("register")

        if entry.code == user_code:
            # Cria o usuário
            data = request.session["register_data"]
            User.objects.create_user(
                email=data["email"],
                password=data["password"],
                name=data["name"],
                phone=data["phone"]
            )

            # Limpa sessão
            del request.session["register_data"]

            messages.success(request, "Conta criada com sucesso! Faça login.")
            return redirect("login")

        else:
            messages.error(request, "Código incorreto.")

    return render(request, "accounts/register_verify.html", {"email": email})
