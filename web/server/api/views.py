from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime


@api_view(["GET"])
def api(request):
    urls = {"name": "Quoc Bao", "dob": "10/10/2000", "time": datetime.now()}
    return Response(urls)
