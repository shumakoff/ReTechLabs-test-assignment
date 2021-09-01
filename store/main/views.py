from datetime import date
from django.db.models.functions import Coalesce
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from main.models import Item, Store
from accounting.models import SupplyLog, SalesLog
from main.serializers import StoreSerializer, StoreItemsSerializer, BuyingSerializer, AddingSerializer


class StoreViewSet(viewsets.ViewSet):
    """
    API endpoint that allows stores to be viewed.
    """

    def list(self, request):
        """
        Shows list of stores
        """
        queryset = Store.objects.all()
        serializer = StoreSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        """
        Shows info about the store
        and what's in store
        """
        store = get_object_or_404(Store.objects.all(), id=pk)
        # all the goods that are in stock
        warehouse = {'store_id': store.id,
                'store_title': store.title,
                'store_items': []}
        items_in_store = SupplyLog.objects.filter(
                date__lte=date.today(),
                store=store).distinct('item')
        for item in items_in_store:
            item_qty_supplied = SupplyLog.objects.filter(
                    date__lte=date.today(),
                    store=store,
                    item_id=item.item.id).aggregate(amount=Coalesce(Sum('qty'), 0))
            item_qty_sold = SalesLog.objects.filter(
                    date__lte=date.today(),
                    store=store,
                    item_id=item.item.id).aggregate(amount=Coalesce(Sum('qty'), 0))
            item_qty_available = item_qty_supplied['amount'] - item_qty_sold['amount']
            if (item_qty_available) >= 1:
                warehouse['store_items'].append(
                        {'item_id': item.id,
                            'qty': item_qty_available,
                            'item_title': item.item.title})
        serializer = StoreItemsSerializer(data=warehouse)
        serializer.is_valid()
        return Response(serializer.data)


    @action(detail=True,
            methods=['POST'],
            url_path='buy')
    def buy(self, request, pk=None):
        store = Store.objects.get(id=pk)
        serializer = BuyingSerializer(data=request.data, context={'store_id': store.id}, many=True)
        if serializer.is_valid():
            for entry in serializer.data:
                item = Item.objects.get(id=entry['product_id'])
                buy_item(store, item, entry['count'])
            return Response({'status': 'transaction successful'})
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True,
            methods=['POST'],
            url_path='add')
    def add(self, request, pk=None):
        store = Store.objects.get(id=pk)
        serializer = AddingSerializer(data=request.data, context={'store_id': store.id}, many=True)
        if serializer.is_valid():
            for entry in serializer.data:
                item = Item.objects.get(id=entry['product_id'])
                add_item(store, item, entry['count'])
            return Response({'status': 'transaction successful'})
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


def buy_item(store, item, qty):
    """
    Make new entry in sales table
    """
    new_entry = SalesLog(date=date.today(), store=store, item=item, qty=qty)
    new_entry.save()


def add_item(store, item, qty):
    """
    Make new entry in supply table
    """
    new_entry = SupplyLog(date=date.today(), store=store, item=item, qty=qty)
    new_entry.save()
