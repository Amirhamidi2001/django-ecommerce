from django import forms
from website.models import Contact, Newsletter


class ContactForm(forms.ModelForm):
    """
    This class is for processing the contact form
    """

    class Meta:
        model = Contact
        fields = "__all__"


class NewsletterForm(forms.ModelForm):
    """
    This class is for processing the Newsletter form
    """

    class Meta:
        model = Newsletter
        fields = ["email"]
