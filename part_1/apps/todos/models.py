from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


# Create your models here.
class Todo(models.Model):
    class STATUS(models.TextChoices):
        DRAFT = "DRAFT"
        SENT = "SENT"
        GENERATED = "GENERATED"

    profile = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="todos")
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS.choices, default=STATUS.DRAFT)
    remind_at = models.DateTimeField()
    image = models.ImageField(upload_to="todos/", blank=True, null=True)
    location_name = models.CharField(max_length=255, default="Windhoek, Namibia")
    latitude = models.FloatField(default=22.5649)
    longitude = models.FloatField(default=17.0842)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("profile", "title")

    def clean(self):
        super().clean()
        now = timezone.now()
        five_minutes_from_now = now + timedelta(minutes=5)

        if self.remind_at < now:
            raise ValidationError("You cannot schedule a reminder for a time in the past.")

        if self.remind_at < five_minutes_from_now:
            raise ValidationError("The reminder must be scheduled at least five minutes from now.")

    def __str__(self):
        return self.title
