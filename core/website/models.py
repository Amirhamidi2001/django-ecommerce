from django.db import models


class Contact(models.Model):
    """
    Represents a contact form submission.
    """

    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the Contact model."""

        ordering = ["-created_at"]

    def __str__(self):
        """Returns the string representation of the contact's name."""
        return self.name


class Newsletter(models.Model):
    """
    Represents a newsletter subscription.
    """

    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Returns the string representation of the subscriber's email."""
        return self.email
