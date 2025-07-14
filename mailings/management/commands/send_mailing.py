from django.core.management.base import BaseCommand
from mailing.models import Mailing
from mailing.tasks import send_mailing_task


class Command(BaseCommand):
    help = "Sends a mailing by ID"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int, help="ID of the mailing to send")

    def handle(self, *args, **options):
        mailing_id = options["mailing_id"]
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
            send_mailing_task.delay(mailing.pk)  # Запускаем задачу Celery асинхронно
            self.stdout.write(
                self.style.SUCCESS(f'Successfully started mailing "{mailing.pk}"')
            )
        except Mailing.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Mailing with id "{mailing_id}" not found')
            )
