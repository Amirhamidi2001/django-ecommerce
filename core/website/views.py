from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib import messages

from .forms import ContactForm, NewsletterForm


class IndexView(TemplateView):
    template_name = "website/index.html"


class AboutView(TemplateView):
    template_name = "website/about.html"


class ContactFormView(FormView):
    template_name = "website/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("website:contact")  # or another URL name

    def form_valid(self, form):
        form.save()  # Save contact form data
        messages.success(self.request, "Your message has been sent successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "There was an error in your submission. Please check the form.",
        )
        return super().form_invalid(form)


class NewsletterSubscribeView(FormView):
    template_name = "website/newsletter.html"
    form_class = NewsletterForm
    success_url = reverse_lazy("website:index")

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, "You've successfully subscribed to the newsletter!"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid email address or already subscribed.")
        return super().form_invalid(form)
