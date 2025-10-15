from django import forms
from django.contrib.auth import authenticate, password_validation
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator

from .models import CustomUser, UserProfile
from .validators import validate_iranian_phone_number


class UserSignUpForm(forms.ModelForm):
    """
    Form for registering a new user.
    """

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm password"}),
    )
    phone_number = forms.CharField(
        label=_("Phone Number"),
        validators=[validate_iranian_phone_number],
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "09xxxxxxxxx"}),
    )

    class Meta:
        model = CustomUser
        fields = ["email", "phone_number"]
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "Enter your email"}),
            "type": forms.Select(),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_("A user with this email already exists."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", _("The two password fields didn’t match."))

        if password1:
            password_validation.validate_password(password1)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """
    Form for logging in an existing user.
    """

    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError(_("Invalid email or password."))
            if not user.is_active:
                raise forms.ValidationError(_("This account is inactive."))

            cleaned_data["user"] = user

        return cleaned_data


class UserPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label=_("Current Password"),
        widget=forms.PasswordInput(attrs={"placeholder": "Enter current password"}),
    )
    new_password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={"placeholder": "Enter new password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm new password"}),
    )

    def __init__(self, user, *args, **kwargs):
        """
        Receives the current user to check the old password.
        """
        self.user = user
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_("Your old password was entered incorrectly."))
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error("new_password2", _("The two password fields didn’t match."))

        if new_password1:
            password_validation.validate_password(new_password1, self.user)

        return cleaned_data

    def save(self, commit=True):
        new_password = self.cleaned_data["new_password1"]
        self.user.set_password(new_password)
        if commit:
            self.user.save()
        return self.user


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"placeholder": "Enter your registered email"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not CustomUser.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError(_("No active user found with this email."))
        return email


class UserPasswordResetForm(forms.Form):
    new_password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={"placeholder": "Enter new password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm new password"}),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("new_password1")
        pw2 = cleaned_data.get("new_password2")
        if pw1 and pw2 and pw1 != pw2:
            self.add_error("new_password2", _("The two password fields didn’t match."))
        password_validation.validate_password(pw1, self.user)
        return cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "bio",
            "profile_picture",
            "birth_date",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
