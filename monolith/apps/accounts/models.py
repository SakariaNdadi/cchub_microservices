from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Profile(AbstractUser):
    contact = PhoneNumberField(region="NA")

    groups = models.ManyToManyField(
        Group,
        verbose_name="groups",
        blank=True,
        help_text=("The groups this user belongs to. A user will get all permissions granted to each of their groups."),
        related_name="profile_groups",
        related_query_name="profile",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="profile_permissions",
        related_query_name="profile",
    )

    def __str__(self):
        return self.username
