# Django
from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'
    verbos_name = "Notepik"

    def ready(self):
        import signals
