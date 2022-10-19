from email.policy import default
from django.db import models


class Video(models.Model):
    name = models.CharField(max_length=50)
    source = models.FileField(upload_to="videos", default=None, blank=True, null=True)

    def __str__(self):
        return f"Video {self.name}"
