from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_password_reset_email_task(self, user_email, reset_url):
    try:
        send_mail(
            subject="Password Reset",
            message=f"Reset your password:\n{reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)