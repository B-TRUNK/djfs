import django_filters
from rest_framework import filters
from fsapp.models import Product

class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        #fields = ['name' ,'price', 'stock']
        fields = {
            'name' :['exact', 'contains'],
            'price' :['exact', 'lt', 'gt', 'range'],
            'stock' :['exact' ,'gt'],
        }

class InStockCustomFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(stock__gt=0) #toggle between filter & exclude
