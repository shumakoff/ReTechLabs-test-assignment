from django.db import models


class Store(models.Model):
    title = models.CharField(max_length=200)


class StoreItems(models.Model):
    parent = models.ForeignKey(Store, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    qty = models.IntegerField()


class Item(models.Model):
    title = models.CharField(max_length=200)
