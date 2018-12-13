from django.core.management.base import BaseCommand

from datasources.models import DataSource


class Command(BaseCommand):
    help = 'Resets external API call count on all data sources'

    def handle(self, *args, **options):
        for datasource in DataSource.objects.all():
            datasource.external_requests = 0
            datasource.save()

            self.stdout.write(self.style.SUCCESS('Successfully reset count for data source "%s"' % datasource.pk))
