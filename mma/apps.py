from django.apps import AppConfig

class MmaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mma'

    def ready(self):
        import mma.signals  # Replace 'mma' with your actual app name