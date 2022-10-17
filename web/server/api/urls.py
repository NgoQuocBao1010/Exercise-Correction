from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.api, name="api"),
    path("/", include("realtime.urls")),
]
