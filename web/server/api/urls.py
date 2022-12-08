from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.api, name="api"),
    path("video/", include("stream_video.urls")),
]
