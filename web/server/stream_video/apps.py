import sys
from django.apps import AppConfig


class StreamVideoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stream_video"

    def ready(self):
        if "runserver" not in sys.argv:
            return True

        from detection.main import load_machine_learning_models

        load_machine_learning_models()
