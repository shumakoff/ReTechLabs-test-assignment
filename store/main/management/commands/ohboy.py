import factory.random
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from tests.factories import ItemFactory, StoreFactory
from accounting.models import SupplyLog, SalesLog


class Command(BaseCommand):
    help = "Populate store with sample data. Generates stores and items"

    def handle(self, *args, **options):

        try:
            with transaction.atomic():

                self._load_fixtures()

        except Exception as e:
            raise CommandError(f"{e}\n\nTransaction was not committed due to the above exception.")

    def _load_fixtures(self):
        """
        Create and save the necessary factories.
        """

        for couner in range(50):
            ItemFactory.create()
        for couner in range(3):
            StoreFactory.create()
