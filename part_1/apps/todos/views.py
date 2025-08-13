from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import TodoForm
from .models import Todo
from .serializers import TodoCompletionSerializer
from .tasks import send_todo_reminder_email


class TodoListView(LoginRequiredMixin, ListView):
    """
    A view to display a list of all todos for the logged-in user.
    """

    model = Todo
    template_name = "todo/list.html"
    context_object_name = "todos"

    def get_queryset(self):
        """
        Ensure users can only see their own todos.
        """
        return Todo.objects.filter(profile=self.request.user)


class TodoDetailView(LoginRequiredMixin, DetailView):
    """
    A view to display a list of all todos for the logged-in user.
    """

    model = Todo
    template_name = "todo/details.html"
    context_object_name = "todo"

    def get_queryset(self):
        """
        Ensure users can only see their own todos.
        """
        return Todo.objects.filter(profile=self.request.user)


class TodoCreateView(LoginRequiredMixin, CreateView):
    """
    A view to create a new todo item.
    """

    model = Todo
    form_class = TodoForm
    template_name = "todo/form.html"
    success_url = reverse_lazy("todo_list")

    def form_valid(self, form):
        """
        Set the profile of the new todo to the currently logged-in user
        and return an HTML partial of the new todo item.
        """
        form.instance.profile = self.request.user
        self.object = form.save()

        return render(self.request, "todo/partials/row.html", {"todo": self.object})


class TodoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    A view to update an existing todo item.
    """

    model = Todo
    form_class = TodoForm
    template_name = "todo/form.html"
    success_url = reverse_lazy("todo_list")

    def test_func(self):
        """
        Ensure users can only update their own todos.
        """
        todo = self.get_object()
        return self.request.user == todo.profile


class TodoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    A view to delete an existing todo item.
    """

    model = Todo
    template_name = ""
    success_url = reverse_lazy("todo_list")

    def test_func(self):
        """
        Ensure users can only delete their own todos.
        """
        todo = self.get_object()
        return self.request.user == todo.profile

    # def delete(self, request, *args, **kwargs):
    #     """
    #     Overrides the default delete method to handle HTMX requests.

    #     Instead of redirecting, it returns an empty 200 OK response and
    #     an 'HX-Trigger' header to fire a client-side event.
    #     """
    #     self.object = self.get_object()
    #     self.object.delete()
    #     response = HttpResponse(status=200)
    #     # response["HX-Trigger"] = "todo-delete"
    #     print("[RESPONSE] ", response)
    #     return response


class CompleteTodoAPIView(APIView):
    """
    Receives the generated notes and image from the Go service
    and updates the Todo item.
    """

    def patch(self, request, todo_id, format=None):
        try:
            todo = Todo.objects.get(pk=todo_id)
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)

        request.data["status"] = Todo.STATUS.GENERATED

        serializer = TodoCompletionSerializer(todo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendTodoEmailAPIView(APIView):
    """
    An API endpoint to manually trigger the sending of a Todo reminder email.
    """

    permission_classes = [AllowAny]

    def post(self, request, todo_id, format=None):
        """
        Triggers the Celery task to send the email for a specific Todo.
        """
        try:
            todo = Todo.objects.get(pk=todo_id)
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)

        if todo.status == Todo.STATUS.SENT:
            return Response({"message": "This email has already been sent."}, status=status.HTTP_400_BAD_REQUEST)

        send_todo_reminder_email.delay(todo.id)

        return Response({"message": "Email sending process has been initiated."}, status=status.HTTP_202_ACCEPTED)
