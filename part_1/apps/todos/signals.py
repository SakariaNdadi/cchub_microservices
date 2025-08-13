from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Todo
from .tasks import process_todo_for_generation


@receiver(post_save, sender=Todo)
def todo_created_handler(sender, instance, created, **kwargs):
    """
    When a new Todo is created, trigger the Celery task.
    """
    if created:
        process_todo_for_generation.delay(instance.id)
