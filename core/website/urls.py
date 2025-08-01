from django.urls import path

from .views import IndexView, AboutView, ContactFormView, NewsletterSubscribeView

app_name = "website"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("about/", AboutView.as_view(), name="about"),
    path("contact/", ContactFormView.as_view(), name="contact"),
    path("newsletter/", NewsletterSubscribeView.as_view(), name="newsletter"),
]
