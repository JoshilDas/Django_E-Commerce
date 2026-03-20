import hashlib
import random
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import PasswordResetToken

from apps.accounts.tasks import send_otp_email_task

from .exceptions import (
    InvalidUserException,
    InvalidOTPException,
    OTPExpiredException,
    OTPBlockedException,
)

# Moving authenticationLogicFrom Serializer to Service
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

OTP_EXPIRY_MINUTES = 2
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
        transaction.on_commit(lambda: send_otp_email_task.delay(user.email, otp))
    except Exception as e:
        # Do NOT break flow (no enumeration, no API failure)
        print(f"[EMAIL ERROR] Failed to send OTP email: {str(e)}")

# -------------------------
# RESET PASSWORD
# -------------------------

def reset_password(email, otp, new_password):

    user = User.objects.filter(email=email).first()

    if not user:
        raise InvalidUserException()

    record = PasswordResetToken.objects.filter(
        user=user,
        is_used=False
    ).order_by("-created_at").first()

    if not record:
        raise InvalidOTPException()

    if record.expires_at < timezone.now():
        raise OTPExpiredException()

    if record.attempt_count >= MAX_OTP_ATTEMPTS:
        raise OTPBlockedException()

    if record.otp_hash != hash_otp(otp):
        PasswordResetToken.objects.filter(id=record.id).update(
            attempt_count=record.attempt_count + 1
        )
        raise InvalidOTPException()

    # ✅ ONLY success path is transactional (DO NOT CHANGE)
    with transaction.atomic():
        record.is_used = True
        record.used_at = timezone.now()
        record.save()

        user.set_password(new_password)
        user.save()

    return user

# -------------------------
# LOGIN
# -------------------------

def login_user(email: str, password: str):
    
    user = authenticate(username=email, password=password)

    if not user:
        raise AuthenticationFailed("Invalid credentials")

    refresh = RefreshToken.for_user(user)

    return {
        "user_id": user.id,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }