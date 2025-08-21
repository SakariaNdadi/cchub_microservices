from django import forms

from .models import Todo


class TodoForm(forms.ModelForm):
    """
    A form for creating and updating Todo instances.
    """

    remind_at = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))

    class Meta:
        model = Todo
        fields = ["title", "description", "remind_at"]
