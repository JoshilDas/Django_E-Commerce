from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from core.api_response import ApiResponse
from core.throttling import LoginIPThrottle

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

#For ForgetPassword
from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer
from .services import handle_forgot_password, reset_password

User = get_user_model()


class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return ApiResponse.created(
            data=UserSerializer(user).data,
            message="User registered successfully",
        )


class LoginView(generics.GenericAPIView):

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    # NEW: IP based throttling applied to login
    throttle_classes = [LoginIPThrottle]

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        access = serializer.validated_data["access"]
        refresh = serializer.validated_data["refresh"]

        return ApiResponse.success(
            data={
                "user": UserSerializer(user).data,
                "access": access,
                "refresh": refresh,
            },
            message="Login successful",
        )


class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user
        serializer = UserSerializer(user)

        return ApiResponse.success(
            data=serializer.data,
            message="User retrieved successfully",
        )

class ForgotPasswordView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        handle_forgot_password(email)

        return ApiResponse.success(
            message="If the account exists, an OTP has been sent to your email."
        )


class ResetPasswordView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        password = serializer.validated_data["new_password"]

        try:
            reset_password(email, otp, password)
        except ValueError as e:
            return ApiResponse.error(
                message="Password reset failed",
                code=str(e)
            )

        return ApiResponse.success(
            message="Password reset successful"
        )


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return ApiResponse.error(
                message="Refresh token required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except Exception:
            return ApiResponse.error(
                message="Invalid or expired token",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        return ApiResponse.success(
            message="Logged out successfully"
        )