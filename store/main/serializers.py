from datetime import date
from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework import serializers
from main.models import Item, Store, StoreItems
from accounting.models import SalesLog, SupplyLog




class StoreSerializer(serializers.ModelSerializer):
    """
    Model Store serializer
    """
    class Meta:
        model = Store
        fields = '__all__'


class ItemSerializer(serializers.Serializer):
    """
    Item serializer for store view
    """
    item_id = serializers.IntegerField()
    item_title = serializers.CharField()
    qty = serializers.IntegerField()


class StoreItemsSerializer(serializers.Serializer):
    """
    StoreViewSet.retrieve serializer
    """
    store_id = serializers.IntegerField()
    store_title = serializers.CharField()
    store_items = ItemSerializer()


class BuyingListSerializer(serializers.ListSerializer):
    """
    Custom ListSerializer.
    Basically to check for non unique product_id
    """


    def validate(self, data):
        """
        Check if we have item with requested id.
        Check if we have enough of requested item at the store.
        """
        # what if fronted will send us multiple JSON
        # records with same product_id
        validation_set = set()

        for item in data:
            if item['product_id'] in validation_set:
                raise serializers.ValidationError('duplicated prouduct_id')
            else:
                validation_set.add(item['product_id'])

            product_id = item['product_id']
            qty_req = item['count']
            store_id = self.context['store_id']
            try:
                item = Item.objects.get(id=product_id)
            except Item.DoesNotExist:
                raise serializers.ValidationError('Requested item id not found')

            # check if we have enough at the specific store warehouse
            # whole order going to fail if one of the product_id availibility
            # is less than ordered amount
            store = Store.objects.get(id=store_id )
            #qty_avail = store.storeitems_set.get(item__id=product_id).qty
            supplied = SupplyLog.objects.filter(date__lte=date.today(), item_id=product_id, store=store).aggregate(supplied=Coalesce(Sum('qty'), 0))
            sold = SalesLog.objects.filter(date__lte=date.today(), item_id=product_id, store=store).aggregate(sold=Coalesce(Sum('qty'), 0))
            qty_avail = supplied['supplied'] - sold['sold']
            if qty_avail < qty_req:
                raise serializers.ValidationError('There is not enough quantity \
                        for item {0}. Qty requested is {1} \
                        and we have only {2}.\
                        '.format(item.title, qty_req, qty_avail))
        return data


class BuyingSerializer(serializers.Serializer):
    """
    Serializer for processing buy requests
    """
    product_id = serializers.IntegerField()
    count = serializers.IntegerField(min_value=1)

    class Meta:
        list_serializer_class = BuyingListSerializer


class AddingSerializer(serializers.Serializer):
    """
    Serializer for processing add requests
    """
    product_id = serializers.IntegerField()
    count = serializers.IntegerField(min_value=1)


    def validate_product_id(self, value):
        """
        Check if we have this product_id in our nomenclature.
        """
        try:
            Item.objects.get(id=value)
            return value
        except Item.DoesNotExist:
            raise serializers.ValidationError('Can\'t add non existent product_id')

