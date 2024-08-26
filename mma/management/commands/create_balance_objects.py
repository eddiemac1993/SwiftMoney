from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mma.models import Balance

User = get_user_model()

class Command(BaseCommand):
    help = 'Create Balance objects for users who do not have one'

    def handle(self, *args, **options):
        users_without_balance = User.objects.filter(balance__isnull=True)
        created_count = 0

        for user in users_without_balance:
            Balance.objects.create(agent=user)
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} Balance objects'))