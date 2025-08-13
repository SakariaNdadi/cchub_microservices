import base64
import mimetypes
import os

import requests
from celery import shared_task
from django.conf import settings

from .models import Todo

# The IP/domain of your Go service
GO_API_URL = os.environ.get("GO_API_URL", "http://localhost:8080") + "/generate-notes"


@shared_task
def process_todo_for_generation(todo_id):
    """
    Fetches a Todo object and sends its data to the Go microservice.
    """
    try:
        todo = Todo.objects.get(id=todo_id)

        payload = {
            "todo_id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "remind_at": todo.remind_at.isoformat(),
            "latitude": todo.latitude,
            "longitude": todo.longitude,
        }

        # Send the data to the Go API
        response = requests.post(GO_API_URL, json=payload, timeout=10)
        response.raise_for_status()

        return f"Successfully sent Todo {todo_id} to Go service."
    except Todo.DoesNotExist:
        return f"Todo with id {todo_id} not found."
    except requests.RequestException as e:
        return f"Failed to send Todo {todo_id} to Go service: {e}"


@shared_task
def send_todo_reminder_email(todo_id):
    """
    Fetches a Todo and sends its details to the Node.js email microservice.
    Upon success, it sets the status to SENT.
    """
    try:
        todo = Todo.objects.get(pk=todo_id)
        user_email = todo.profile.email

        image_data = {}
        if todo.image:
            filename = os.path.basename(todo.image.name)
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            image_content = todo.image.read()
            base64_content = base64.b64encode(image_content).decode("utf-8")

            image_data = {
                "imageBase64": base64_content,
                "imageFilename": filename,
                "imageContentType": content_type,
            }

        payload = {
            "to": user_email,
            "title": todo.title,
            "description": todo.description,
            "notes": todo.notes,
            **image_data,
        }

        email_service_url = settings.EMAIL_SERVICE_URL
        response = requests.post(email_service_url, json=payload)
        response.raise_for_status()

        # This is where the status is set to SENT as you requested
        todo.status = Todo.STATUS.SENT
        todo.save(update_fields=["status"])

        return f"Successfully sent reminder for Todo {todo.id}"
    except Todo.DoesNotExist:
        return f"Todo with id {todo_id} not found."
    # except requests.exceptions.RequestException as e:
    #     raise self.retry(exc=e, countdown=60)
