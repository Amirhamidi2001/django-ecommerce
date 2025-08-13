from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .validators import validate_iranian_phone_number


class UserType(models.IntegerChoices):
    CUSTOMER = 1, _("customer")
    ADMIN = 2, _("admin")
    SUPERUSER = 3, _("superuser")


class CustomUserManager(BaseUserManager):
    """
    Manager for CustomUser.

    - create_user: allows creating users with or without a password. If password is None,
      an unusable password is set (useful for social accounts).
    - create_superuser: enforces is_staff/is_superuser and requires a password.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            # No password provided: make account unusable (e.g. for OAuth-only accounts)
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser. A password is required for superusers.
        Extra_fields are validated to ensure the account is actually a superuser.
        """
        if not password:
            raise ValueError(_("Superusers must have a password."))

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("type", UserType.SUPERUSER)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses email as the unique identifier.
    """

    email = models.EmailField(_("email address"), unique=True, db_index=True)
    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    is_verified = models.BooleanField(_("verified"), default=False)
    type = models.IntegerField(
        _("user type"), choices=UserType.choices, default=UserType.CUSTOMER
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    Extended profile for user-specific metadata.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    # Allow formats like: +98912xxxxxxx or 0912xxxxxxx -> size 14 covers plus and country code
    phone_number = models.CharField(
        _("phone number"),
        max_length=14,
        validators=[validate_iranian_phone_number],
        blank=True,
        null=True,
        help_text=_("Accepts formats like +98912xxxxxxx or 0912xxxxxxx"),
    )
    first_name = models.CharField(
        _("first name"), max_length=30, blank=True, default=""
    )
    last_name = models.CharField(_("last name"), max_length=30, blank=True, default="")
    bio = models.TextField(_("bio"), blank=True, null=True)
    profile_picture = models.ImageField(
        _("profile picture"),
        upload_to="profiles/%Y/%m/%d/",
        blank=True,
        null=True,
    )
    birth_date = models.DateField(_("birth date"), blank=True, null=True)

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

    def __str__(self):
        # Prefer full name if present, otherwise show the user's email
        full = self.get_fullname()
        return (
            full if full != "New User" else getattr(self.user, "email", str(self.user))
        )

    def get_fullname(self):
        name_parts = [self.first_name.strip(), self.last_name.strip()]
        full_name = " ".join(part for part in name_parts if part)
        return full_name or "New User"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a profile whenever a new user is created.
    Using settings.AUTH_USER_MODEL avoids a direct import-cycle.
    """
    if created:
        # Avoid double-creation if some external flow created profile already
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, created, **kwargs):
    """
    Ensure profile is saved when user is saved (useful if profile fields depend on user).
    Not always necessary but harmless.
    """
    if not created:
        # Only attempt to save if profile exists to avoid creating a blank profile by accident
        try:
            profile = instance.profile
            profile.save()
        except UserProfile.DoesNotExist:
            # If you'd rather auto-create on any save, uncomment the next line:
            # UserProfile.objects.create(user=instance)
            pass
