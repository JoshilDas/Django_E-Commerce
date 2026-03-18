from django.db import models
from core.models import BaseModel
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("CUSTOMER", "Customer"),
    )

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="CUSTOMER"
    )

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


# Adding Forget Password Functionalities with OTP

class PasswordResetToken(BaseModel):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens"
    )

    otp_hash = models.CharField(max_length=128)

    expires_at = models.DateTimeField()

    is_used = models.BooleanField(default=False)

    used_at = models.DateTimeField(null=True, blank=True)

    attempt_count = models.IntegerField(default=0)

    class Meta:
        db_table = "password_reset_tokens"
        indexes = [
            models.Index(fields=["user", "is_used"]),
        ]