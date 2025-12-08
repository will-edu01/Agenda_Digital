import random
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from django.http import JsonResponse
from .models_verification import VerificationCode
from .forms import RegisterForm
from accounts.models import User



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
            return redirect("verify_email")
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
        print("CÓDIGO RECEBIDO:", user_code)

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
            data = request.session["register_data"]
            User.objects.create_user(
                email=data["email"],
                password=data["password"],
                name=data["name"],
                phone=data["phone"],
            )
            try:
                entry.mark_used()
            except Exception:
                entry.is_used = True
                entry.save(update_fields=['is_used'])

            del request.session["register_data"]

            return render(request, "accounts/register_verify.html", {
                "email": email,
                "verified": True
            })

        else:
            messages.error(request, "Código incorreto.")

    return render(request, "accounts/register_verify.html", {"email": email})


def resend_verification_code(request):
    if "register_data" not in request.session:
        return JsonResponse({"ok": False, "error": "Sessão expirada."}, status=400)

    email = request.session["register_data"]["email"]

    # Gera novo código
    code = f"{random.randint(100000, 999999)}"
    
    VerificationCode.objects.create(email=email, code=code)

    # Envia email
    send_mail(
        "Seu novo código de verificação",
        f"Seu novo código é: {code}",
        settings.EMAIL_HOST_USER,
        [email],
    )

    return JsonResponse({"ok": True})
