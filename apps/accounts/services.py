import hashlib
import random
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import PasswordResetToken
from core.email import send_otp_email

User = get_user_model()

OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 5


# -------------------------
# OTP HELPERS
# -------------------------

def generate_otp():
    return str(random.randint(100000, 999999))


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


# -------------------------
# FORGOT PASSWORD
# -------------------------

def create_otp(user):

    # invalidate old OTPs
    PasswordResetToken.objects.filter(
        user=user,
        is_used=False
    ).update(is_used=True)

    otp = generate_otp()
    otp_hash = hash_otp(otp)

    expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    PasswordResetToken.objects.create(
        user=user,
        otp_hash=otp_hash,
        expires_at=expires_at
    )

    return otp


def handle_forgot_password(email):
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return

    otp = create_otp(user)

    # Send OTP via email
    try:
        send_otp_email(user.email, otp)
    except Exception as e:
        # Do NOT break flow (no enumeration, no API failure)
        print(f"[EMAIL ERROR] Failed to send OTP email: {str(e)}")

# -------------------------
# RESET PASSWORD
# -------------------------

def reset_password(email, otp, new_password):

    user = User.objects.filter(email=email).first()

    if not user:
        raise ValueError("INVALID_USER")

    record = PasswordResetToken.objects.filter(
        user=user,
        is_used=False
    ).order_by("-created_at").first()

    if not record:
        raise ValueError("INVALID_OTP")

    if record.expires_at < timezone.now():
        raise ValueError("OTP_EXPIRED")

    if record.attempt_count >= MAX_OTP_ATTEMPTS:
        raise ValueError("OTP_BLOCKED")

    if record.otp_hash != hash_otp(otp):
        PasswordResetToken.objects.filter(id=record.id).update(
            attempt_count=record.attempt_count + 1
        )
        raise ValueError("INVALID_OTP")

    # ✅ Only success path needs transaction
    with transaction.atomic():
        record.is_used = True
        record.used_at = timezone.now()
        record.save()

        user.set_password(new_password)
        user.save()

    return user