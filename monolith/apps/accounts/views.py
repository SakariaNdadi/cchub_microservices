from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView

from .forms import ProfileChangeForm, ProfileCreationForm
from .models import Profile

# Create your views here.


class SignUpView(CreateView):
    """
    A view for new users to sign up.
    Uses the ProfileCreationForm and redirects to the login page upon
    successful registration.
    """

    form_class = ProfileCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    A view for users to update their own profile information.
    This view is protected and requires the user to be logged in.
    It ensures that users can only edit their own profile.
    """

    model = Profile
    form_class = ProfileChangeForm
    template_name = "profile_update.html"
    success_url = reverse_lazy("home")

    def get_object(self, queryset=None):
        """
        This method ensures that the user editing the profile
        is the currently logged-in user.
        """
        return self.request.user
