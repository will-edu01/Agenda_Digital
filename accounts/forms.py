from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    email = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={"placeholder": "E-mail", "class": "input-field"}))
    password = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={"placeholder": "Senha", "class": "input-field"}))
    remember_me = forms.BooleanField(required=False, label="Lembrar-me")


    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        user = authenticate(email=email, password=password)

        if user is None:
            raise forms.ValidationError("E-mail ou senha inválidos.")

        cleaned_data["user"] = user
        return cleaned_data
    

class RegisterForm(forms.Form):
    name = forms.CharField(label="Nome", max_length=150)
    email = forms.EmailField(label="E-mail")
    phone = forms.CharField(label="WhatsApp", max_length=20)
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirmar Senha", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        from accounts.models import User
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")

        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data
