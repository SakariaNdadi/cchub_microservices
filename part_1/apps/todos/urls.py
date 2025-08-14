from django.urls import path

from .views import (
    TodoCreateView,
    TodoDeleteView,
    TodoDetailView,
    TodoListView,
    TodoUpdateView,
)

urlpatterns = [
    path("", TodoListView.as_view(), name="todo_list"),
    path("new/", TodoCreateView.as_view(), name="todo_new"),
    path("details/<int:pk>/", TodoDetailView.as_view(), name="todo_detail"),
    path("edit/<int:pk>/", TodoUpdateView.as_view(), name="todo_edit"),
    path("delete/<int:pk>/", TodoDeleteView.as_view(), name="todo_delete"),
]
