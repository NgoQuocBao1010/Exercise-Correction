from django.shortcuts import render


def render_client(request):
    return render(request, template_name="index.html")
