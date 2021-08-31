from django.db import models


class Item(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
            return self.title

class Store(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
            return self.title


class StoreItems(models.Model):
    parent = models.ForeignKey(Store, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    qty = models.IntegerField()

    def __str__(self):
            return 'Items at %s' % self.parent.title
