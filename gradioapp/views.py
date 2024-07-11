# gradioapp/views.py
from django.shortcuts import render

def gradio_view(request):
    return render(request, 'gradioapp/gradio.html')