from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.urls import reverse

from .models import CustomUser

signer = TimestampSigner()


def generate_email_confirmation_token(user):
    return signer.sign(user.email)


def verify_email_token(token, max_age=60 * 60 * 24):
    try:
        email = signer.unsign(token, max_age=max_age)
        return CustomUser.objects.get(email=email)
    except (BadSignature, SignatureExpired, CustomUser.DoesNotExist):
        return None


def get_confirmation_link(request, user):
    from django.utils.http import urlencode

    token = generate_email_confirmation_token(user)
    url = request.build_absolute_uri(
        reverse("accounts:verify-email") + f"?{urlencode({'token': token})}"
    )
    return url
