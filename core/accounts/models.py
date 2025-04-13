from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from accounts.validators import validate_iranian_cellphone_number

# UserType Enum - Simplified and clear.
class UserType(models.IntegerChoices):
    """
    Enumeration class to define types of users in the system.
    """
    CUSTOMER = 1, _("Customer")
    ADMIN = 2, _("Admin")
    SUPERUSER = 3, _("Superuser")

# Custom User Manager
class UserManager(BaseUserManager):
    """
    Custom manager class to handle User creation and management.
    """
    def create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("type", UserType.SUPERUSER.value)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)

# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model extending Django's AbstractBaseUser and PermissionsMixin.
    """
    email = models.EmailField(_("Email address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    type = models.IntegerField(choices=UserType.choices, default=UserType.CUSTOMER.value)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

# Profile model
class Profile(models.Model):
    """
    Profile model to store additional user information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=12, validators=[validate_iranian_cellphone_number])
    image = models.ImageField(upload_to="profile/", default="profile/default.png")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_fullname(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else "New User"

# Automatically create a Profile when a User is created.
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Django signal to automatically create a Profile for every new User.
    """
    if created:
        Profile.objects.get_or_create(user=instance)
