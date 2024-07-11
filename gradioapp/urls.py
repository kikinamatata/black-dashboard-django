from django.urls import path
from . import views

urlpatterns = [
    path('gradio/', views.gradio_view, name='gradio_view'),
]