from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_appointment_confirmation(user, services, date, time, total_price):

    subject = "🌸 Seu agendamento foi confirmado!"
    from_email = "SEU_EMAIL_AQUI"
    to = [user.email]

    html_content = render_to_string("emails/appointment_confirmation.html", {
        "user_name": user.name or user.email,
        "services": services,
        "date": date,
        "time": time,
        "total_price": total_price,
    })

    msg = EmailMultiAlternatives(subject, "", from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    