from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail

from .forms import (
    UserSignUpForm,
    UserLoginForm,
    UserPasswordChangeForm,
    PasswordResetRequestForm,
    UserPasswordResetForm,
    UserProfileForm,
)
from .emails import send_verification_email
from .utils import verify_email_token
from .models import CustomUser, UserProfile


class RegisterView(FormView):
    """
    Handles user registration and sends an email verification link.
    """

    template_name = "accounts/register.html"
    form_class = UserSignUpForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_verified = False
        user.is_active = False  # inactive until verified
        user.save()

        send_verification_email(self.request, user)
        messages.success(
            self.request,
            _(
                "We’ve sent you a verification email. Please confirm your email to activate your account."
            ),
        )
        return super().form_valid(form)


class VerifyEmailView(View):
    """
    Handles email verification links.
    """

    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        user = verify_email_token(token)

        if user:
            user.is_verified = True
            user.is_active = True
            user.save()
            messages.success(
                request, _("Your email has been verified. You can now log in.")
            )
            return redirect("accounts:login")

        messages.error(request, _("Verification link is invalid or expired."))
        return redirect("accounts:register")


class LoginView(FormView):
    """
    Handles user login with email verification check.
    """

    template_name = "accounts/login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("website:index")

    def form_valid(self, form):
        user = form.cleaned_data.get("user")

        if not user.is_verified:
            messages.error(
                self.request, _("Please verify your email before logging in.")
            )
            return redirect("accounts:login")

        login(self.request, user)
        messages.success(self.request, _("Welcome back!"))
        return super().form_valid(form)


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)


class ChangePasswordView(LoginRequiredMixin, FormView):
    """
    Allows logged-in users to change their password.
    """

    template_name = "accounts/change_password.html"
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("website:index")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, self.request.user)  # Keep user logged in
        messages.success(
            self.request, _("Your password has been changed successfully.")
        )
        return super().form_valid(form)


class PasswordForgotView(FormView):
    template_name = "accounts/forgot_password.html"
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = CustomUser.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = self.request.build_absolute_uri(
            reverse_lazy(
                "accounts:reset-password", kwargs={"uidb64": uid, "token": token}
            )
        )

        send_mail(
            subject=_("Reset your password"),
            message=_(
                f"Hi {user.email},\n\nClick the link below to reset your password:\n"
                f"{reset_url}\n\nIf you didn’t request a password reset, please ignore this email."
            ),
            from_email=None,
            recipient_list=[user.email],
        )

        messages.success(
            self.request,
            _("We’ve sent a password reset link to your email address."),
        )
        return super().form_valid(form)


class PasswordResetView(FormView):
    template_name = "accounts/reset-password.html"
    form_class = UserPasswordResetForm
    success_url = reverse_lazy("accounts:login")

    def get_user(self, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return None

    def dispatch(self, request, *args, **kwargs):
        self.user = self.get_user(kwargs.get("uidb64"))
        self.token = kwargs.get("token")

        if self.user is None or not default_token_generator.check_token(
            self.user, self.token
        ):
            messages.error(request, _("Invalid or expired password reset link."))
            return redirect("accounts:forgot-password")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            _("Your password has been reset successfully. You can now log in."),
        )
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    template_name = "accounts/profile.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)
