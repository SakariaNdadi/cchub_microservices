from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import Todo


class TodoCompletionSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)

    class Meta:
        model = Todo
        fields = ["notes", "image", "status"]
