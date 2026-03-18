from django.core.mail import send_mail
from django.conf import settings


def send_otp_email(email: str, otp: str):
    subject = "Your Password Reset OTP"
    
    message = f"""
Your OTP for password reset is: {otp}

This OTP will expire in 10 minutes.

If you did not request this, please ignore this email.
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )