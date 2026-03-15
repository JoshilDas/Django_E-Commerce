from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from core.responses import success_response
from core.throttling import LoginIPThrottle   # NEW IMPORT


User = get_user_model()


class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return success_response(
            data=UserSerializer(user).data,
            message="User registered successfully",
            status=status.HTTP_201_CREATED,
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

        return success_response(
            data={
                "user": UserSerializer(user).data,
                "access": access,
                "refresh": refresh,
            },
            message="Login successful",
            status=status.HTTP_200_OK,
        )


class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user
        serializer = UserSerializer(user)

        return success_response(
            data=serializer.data,
            message="User retrieved successfully",
        )