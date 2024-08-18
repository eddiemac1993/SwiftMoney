# mma/apps.py

from django.apps import AppConfig

class MmaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mma'

    def ready(self):
        from . import schedulers
        schedulers.start()