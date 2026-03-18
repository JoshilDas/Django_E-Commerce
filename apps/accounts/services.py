import hashlib
import secrets
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import PasswordResetToken
from .tasks import send_password_reset_email_task

User = get_user_model()

PASSWORD_RESET_EXPIRY_MINUTES = 15


def generate_raw_token():
    return secrets.token_urlsafe(48)


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def create_password_reset_token(user):

    # Invalidate old tokens
    PasswordResetToken.objects.filter(
        user=user,
        is_used=False
    ).update(is_used=True)

    raw_token = generate_raw_token()
    token_hash = hash_token(raw_token)

    expires_at = timezone.now() + timedelta(minutes=PASSWORD_RESET_EXPIRY_MINUTES)

    PasswordResetToken.objects.create(
        user=user,
        token_hash=token_hash,
        expires_at=expires_at
    )

    return raw_token


def send_password_reset_email(user, raw_token):
    from django.conf import settings

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"

    send_password_reset_email_task(
        user_email=user.email,
        reset_url=reset_url
    )


def handle_forgot_password(email):
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return

    raw_token = create_password_reset_token(user)
    send_password_reset_email(user, raw_token)


@transaction.atomic
def reset_password(raw_token, new_password):

    token_hash = hash_token(raw_token)

    token = PasswordResetToken.objects.select_for_update().select_related("user").filter(
        token_hash=token_hash
    ).first()

    if not token:
        raise ValueError("INVALID_TOKEN")

    if token.is_used:
        raise ValueError("TOKEN_USED")

    if token.expires_at < timezone.now():
        raise ValueError("TOKEN_EXPIRED")

    if not token.user.is_active:
        raise ValueError("USER_INACTIVE")

    # mark used immediately
    token.is_used = True
    token.used_at = timezone.now()
    token.save()

    user = token.user
    user.set_password(new_password)
    user.save()

    return user