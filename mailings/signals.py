from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver


def start_scheduler():
    scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
    scheduler.start()


@receiver(post_migrate)
def init_scheduler(sender, **kwargs):
    if sender.name == "mailing":
        start_scheduler()
