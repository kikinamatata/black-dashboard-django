from django.apps import AppConfig
from .client import start_gradio_interface

class GradioappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gradioapp'

    def ready(self):
        start_gradio_interface()