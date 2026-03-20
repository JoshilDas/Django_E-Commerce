from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
        )

    def create(self, validated_data):

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )

        return user

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "role",
            "created_at",
        )

class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # ✅ PURE VALIDATION ONLY
        return data

# Adding ForgetPassword Functionalities

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower().strip()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        if not attrs.get("email"):
            raise serializers.ValidationError("Email is required")

        if not attrs.get("otp"):
            raise serializers.ValidationError("OTP is required")

        if not attrs.get("new_password"):
            raise serializers.ValidationError("Password is required")

        return attrs