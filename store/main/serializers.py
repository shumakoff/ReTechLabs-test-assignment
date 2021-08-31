from rest_framework import serializers
from main.models import Item, Store, StoreItems


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'



class StoreItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreItems
        fields = '__all__'


class BuyingListSerializer(serializers.ListSerializer):


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
            # whole order going to fail if one of the product_id is less
            # than ordered amount
            store = Store.objects.get(id=store_id )
            qty_avail = store.storeitems_set.get(id=product_id).qty
            if qty_avail < qty_req:
                raise serializers.ValidationError('There is not enough quantity \
                        for item {0}. Qty requested is {1} \
                        and we have only {2}.\
                        '.format(item.title, qty_req, qty_avail))
        return data


class BuyingSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    count = serializers.IntegerField()

    class Meta:
        list_serializer_class = BuyingListSerializer


class AddingSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    count = serializers.IntegerField()


    def validate_product_id(self, value):
        """
        Check if we have this product_id in our nomenclature.
        """
        try:
            item = Item.objects.get(id=value)
            return value
        except Item.DoesNotExist:
            raise serializers.ValidationError('Can\'t add non existent product_id')

