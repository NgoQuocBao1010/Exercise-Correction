from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Match all other routes for Frontend to handle
urlpatterns += [
    path("", TemplateView.as_view(template_name="index.html"), {"resource": ""}),
    path("<path:resource>", TemplateView.as_view(template_name="index.html")),
]
