from django.core.exceptions import ValidationError
import re

def validate_iranian_cellphone_number(value):
    """Validator for Iranian cellphone numbers."""
    pattern = r'^09\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError('Enter a valid Iranian cellphone number.')
