from celery import shared_task
import logging
from core.email import send_otp_email

from django.utils import timezone
from apps.accounts.models import PasswordResetToken

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def debug_task(self):
    logger.info("Celery debug task executed")
    return "OK"

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def send_otp_email_task(self, email, otp):
    send_otp_email(email, otp)


@shared_task
def cleanup_expired_otps():
    now = timezone.now()

    deleted, _ = PasswordResetToken.objects.filter(
        expires_at__lt=now
    ).delete()

    return f"Deleted {deleted} expired OTPs"