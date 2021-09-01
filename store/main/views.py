from datetime import date
from django.shortcuts import render, get_object_or_404
from django.core import serializers
from django.db import transaction
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from main.models import Item, Store, StoreItems
from accounting.models import SupplyLog, SalesLog
from main.serializers import StoreSerializer, StoreItemsSerializer, BuyingSerializer, AddingSerializer


class StoreViewSet(viewsets.ViewSet):
    """
    API endpoint that allows stores to be viewed.
    """

    def list(self, request):
        queryset = Store.objects.all()
        serializer = StoreSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        store = Store.objects.get(id=pk)
        # all the goods that are in stock
        warehouse = store.storeitems_set.all().filter(qty__gt=0)
        serializer = StoreItemsSerializer(warehouse, many=True)
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
        else:
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
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


def buy_item(store, item, qty):
    new_entry = SalesLog(date=date.today(), store=store, item=item, qty=qty)
    new_entry.save()


def add_item(store, item, qty):
    new_entry = SupplyLog(date=date.today(), store=store, item=item, qty=qty)
    new_entry.save()
