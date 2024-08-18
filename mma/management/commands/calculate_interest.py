from django.core.management.base import BaseCommand
from mma.views import calculate_interest

class Command(BaseCommand):
    help = 'Calculate daily interest for all agents'

    def handle(self, *args, **options):
        calculate_interest()
        self.stdout.write(self.style.SUCCESS('Successfully calculated interest'))