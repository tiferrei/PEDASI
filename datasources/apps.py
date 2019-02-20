import logging

from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError


logger = logging.getLogger(__name__)


class DatasourcesConfig(AppConfig):
    name = 'datasources'

    @staticmethod
    def create_operational_metadata():
        from datasources.models import MetadataField

        MetadataField.load_inline_fixtures()

    def ready(self):
        # Runs after app registry is populated - i.e. all models exist and are importable
        try:
            self.create_operational_metadata()
            logging.info('Loaded inline MetadataField fixtures')

        except (OperationalError, ProgrammingError):
            logging.warning('Could not create MetadataField fixtures, database has not been initialized')
