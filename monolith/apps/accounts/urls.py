from django.urls import include, path

from .views import ProfileUpdateView, SignUpView

# app_label = "accounts"

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/", ProfileUpdateView.as_view(), name="profile_update"),
]
