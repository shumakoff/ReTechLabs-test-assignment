from datetime import date
from django.db.models.functions import Coalesce
from django.db.models import Sum
from django.test import TestCase
from tests.factories import ItemFactory, StoreFactory, random_string
from accounting.models import SupplyLog, SalesLog
from main.views import add_item, buy_item


class ItemTestCase(TestCase):
    def test_item_creation(self):
        for counter in range(50):
            title = random_string()
            item = ItemFactory.create(title=title)
            self.assertEqual(item.title, title)


class StoreTestCase(TestCase):
    def test_store_creation(self):
        for counter in range(10):
            title = random_string()
            store = StoreFactory.create(title=title)
            self.assertEqual(store.title, title)


class SupplyTestCase(TestCase):
    def setUp(self):
        self.store = StoreFactory()
        self.item = ItemFactory()
        self.QTY_1 = 5
        self.QTY_2 = 15

    def test_supply(self):
        add_item(self.store, self.item, self.QTY_1)
        supplied = SupplyLog.objects.filter(
                date__lte=date.today(),
                item=self.item,
                store=self.store
                ).aggregate(supplied=Coalesce(Sum('qty'), 0))
        self.assertEqual(supplied['supplied'], self.QTY_1)

        add_item(self.store, self.item, self.QTY_2)
        supplied = SupplyLog.objects.filter(
                date__lte=date.today(),
                item=self.item,
                store=self.store
                ).aggregate(supplied=Coalesce(Sum('qty'), 0))
        self.assertEqual(supplied['supplied'], self.QTY_2+self.QTY_1)

    def test_buy(self):
        buy_item(self.store, self.item, self.QTY_2)
        buy_item(self.store, self.item, self.QTY_1)
        sold = SalesLog.objects.filter(
                date__lte=date.today(),
                item=self.item,
                store=self.store
                ).aggregate(sold=Coalesce(Sum('qty'), 0))
        self.assertEqual(sold['sold'], self.QTY_2+self.QTY_1)

