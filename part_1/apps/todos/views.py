from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView


from .forms import TodoForm
from .models import Todo


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
