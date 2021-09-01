from django.db import models


class Item(models.Model):
    """
    Model for items
    """
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Store(models.Model):
    """
    Model for stores
    """
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class StoreItems(models.Model):
    """
    To bind item, store it's located and quantity.
    Not used
    """
    parent = models.ForeignKey(Store, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    qty = models.IntegerField()

    def __str__(self):
        return '%s of %s in %s' % (self.qty, self.item, self.parent.title)
