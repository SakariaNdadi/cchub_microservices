from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/todos/", permanent=True)),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("todos/", include("apps.todos.urls")),
]

if settings.DEBUG:
    urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
