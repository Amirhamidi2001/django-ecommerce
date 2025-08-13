import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

IRAN_PHONE_RE = re.compile(r"^(?:\+98|0)?9\d{9}$")


def validate_iranian_phone_number(value):
    if not value:
        return
    digits = value.replace(" ", "").replace("-", "")
    if not IRAN_PHONE_RE.match(digits):
        raise ValidationError(_("Enter a valid Iranian phone number."))
