from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from phonenumber_field.formfields import PhoneNumberField

from .models import Profile


class ProfileCreationForm(UserCreationForm):
    """
    A form for creating new users. Includes the custom 'contact' field
    and makes the email field required.
    """

    email = forms.EmailField(required=True, help_text="Required. A valid email address.")
    contact = PhoneNumberField(widget=forms.TextInput, help_text="Required. A valid Namibian number.")

    class Meta(UserCreationForm.Meta):
        model = Profile
        fields = ("username", "email", "contact")


class ProfileChangeForm(UserChangeForm):
    """
    A form for updating an existing user's profile. Includes the 'contact' field
    and makes the email field required.
    """

    email = forms.EmailField(required=True, help_text="Required. A valid email address.")
    contact = PhoneNumberField(widget=forms.TextInput, help_text="Required. A valid Namibian number.")

    class Meta:
        model = Profile
        fields = ("username", "email", "contact")
