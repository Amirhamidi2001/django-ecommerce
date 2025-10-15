from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

from .utils import get_confirmation_link


def send_verification_email(request, user):
    subject = _("Verify your email address")
    message = _(
        f"Hi {user.email},\n\n"
        f"Please click the link below to verify your email:\n"
        f"{get_confirmation_link(request, user)}\n\n"
        f"If you didn’t create an account, ignore this message."
    )
    send_mail(subject, message, None, [user.email])
