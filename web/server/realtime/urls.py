from django.urls import path
from . import views

urlpatterns = [
    path("realtime", views.realtime, name="realtime"),
]
