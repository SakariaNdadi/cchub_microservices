from django.db import models

# Create your models here.


class GoServiceLogs(models.Model):
    class STATUS(models.TextChoices):
        FAILED = "FAILED"
        SUCCESSFUL = "SUCCESSFUL"

    todo = models.PositiveBigIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    remind_at = models.DateTimeField()
    weather_status = models.CharField(max_length=255)
    notes = models.CharField(max_length=500)
    image_prompt = models.CharField(max_length=500)
    status = models.CharField(max_length=10, choices=STATUS.choices, default="")
