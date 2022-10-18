import os
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings


@api_view(["GET"])
def api(request):
    path = f"{settings.MEDIA_ROOT}/plank1.mp4"
    video_size = os.path.getsize(path)

    chunk_size = 8000

    response = StreamingHttpResponse(
        FileWrapper(open(path, "rb"), chunk_size), content_type="video/mp4"
    )

    response["Content-Length"] = video_size
    return response
