from django.apps import AppConfig

class MmaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mma'

    def ready(self):
        # Comment out or remove the scheduler start call if it's no longer needed
        # from . import schedulers
        # schedulers.start()
        pass
