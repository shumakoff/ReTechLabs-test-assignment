import string
import random
import factory
from main.models import Item, Store


def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))

class ItemFactory(factory.django.DjangoModelFactory):
    title = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = Item


class StoreFactory(factory.django.DjangoModelFactory):
    title = factory.LazyAttribute(lambda t: random_string())

    class Meta:
        model = Store
