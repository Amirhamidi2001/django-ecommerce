from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "is_staff", "is_verified", "is_active", "type")
    list_filter = ("is_staff", "is_verified", "is_active", "type")
    search_fields = ("email",)
    ordering = ("email",)

    fieldsets = (
        ("Authentication", {"fields": ("email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_verified",
                    "is_superuser",
                    "type",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_verified",
                    "is_superuser",
                    "type",
                ),
            },
        ),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]


class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    list_display = (
        "user",
        "phone_number",
        "first_name",
        "last_name",
        "bio",
        "birth_date",
        "profile_picture",
    )
    search_fields = ("user__email", "first_name", "last_name")
    list_filter = ("user__type",)


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
