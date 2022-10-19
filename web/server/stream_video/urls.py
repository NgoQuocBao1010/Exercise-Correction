from django.urls import path
from . import views

urlpatterns = [
    path("", views.api, name="video"),
    path("upload", views.upload_video, name="upload"),
]
