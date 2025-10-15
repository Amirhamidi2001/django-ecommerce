from django.urls import path
from .views import *

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("forgot-password/", PasswordForgotView.as_view(), name="forgot-password"),
    path(
        "reset-password/<uidb64>/<token>/",
        PasswordResetView.as_view(),
        name="reset-password",
    ),
    path("profile/", ProfileView.as_view(), name="profile"),
]
