import django_filters
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