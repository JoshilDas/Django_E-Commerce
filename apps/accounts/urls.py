from django.urls import path

from .views import RegisterView, LoginView, MeView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ForgotPasswordView, ResetPasswordView


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/forgot-password/", ForgotPasswordView.as_view()),
    path("auth/reset-password/", ResetPasswordView.as_view()),
]