from django.db import models
from main.models import Store, Item


class SalesLog(models.Model):
    """
    Class for storing sold items in specific store
    """
    date = models.DateField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    qty = models.IntegerField()


    def __str__(self):
        return 'Sold %s items of %s on %s in %s' % (
                self.qty, self.item, self.date, self.store.title)


class SupplyLog(models.Model):
    """
    Class for storing items that got supplied to the specific store
    """
    date = models.DateField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    qty = models.IntegerField()


    def __str__(self):
        return 'Received %s items of %s on %s in %s' % (
                self.qty, self.item, self.date, self.store.title)
