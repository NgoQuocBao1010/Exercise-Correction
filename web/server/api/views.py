from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def api(request):
    urls = {"name": "Quoc Bao", "dob": "10/10/2000"}
    return Response(urls)
