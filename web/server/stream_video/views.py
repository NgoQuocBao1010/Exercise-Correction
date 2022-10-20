import os
import mimetypes
from wsgiref.util import FileWrapper

from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django.templatetags.static import static
from django.http import StreamingHttpResponse
from django.conf import settings
from django.http import JsonResponse

from detection.main import bicep_detection


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
        FileWrapper(open(path, "rb"), chunk_size), content_type=content_type
    )
    response["Content-Length"] = video_size
    response["Accept-Ranges"] = "bytes"
    return response


@api_view(["POST"])
@parser_classes([MultiPartParser])
def upload_video(request):
    try:
        if request.method == "POST":
            video = request.FILES["file"]
            bicep_detection(video.temporary_file_path(), video.name)

            processed_video_url = f"{request.get_host()}{static(f'media/{video.name}')}"

            return JsonResponse(
                status=status.HTTP_200_OK,
                data={"file_name": processed_video_url},
            )

    except Exception as e:
        return JsonResponse(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            data={
                "error": f"Error: {e}",
            },
        )
