import os
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

from detection.main import bicep_detection
import mimetypes


@api_view(["GET"])
def api(request):
    og_path = f"{settings.MEDIA_ROOT}/plank1.mp4"
    bicep_detection(og_path)

    path = f"{settings.MEDIA_ROOT}/output.mp4"
    video_size = os.path.getsize(path)

    content_type, _ = mimetypes.guess_type(path)
    content_type = content_type or "application/octet-stream"

    chunk_size = video_size // 10

    response = StreamingHttpResponse(
        FileWrapper(open(path, "rb"), video_size), content_type=content_type
    )
    response["Content-Length"] = video_size
    response["Accept-Ranges"] = "bytes"
    return response
