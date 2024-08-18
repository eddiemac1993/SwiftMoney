# mma/schedulers.py

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
import sys

from .views import calculate_interest

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Run calculate_interest() every day at midnight
    scheduler.add_job(
        calculate_interest,
        trigger='cron',
        hour=0,
        minute=0,
        jobstore='default',
        id='calculate_daily_interest',
        max_instances=1,
        replace_existing=True,
    )

    scheduler.start()
    print("Scheduler started...", file=sys.stdout)