from fsapp.serializers import *
from fsapp.models import *
from django.shortcuts import get_object_or_404
#1
from django.http import JsonResponse
#2
from rest_framework.response import Response
from rest_framework.decorators import api_view
#3
from .serializers import ProductInfoSerializer
from django.db.models import Max
#4
from rest_framework import generics
# Authentication
from rest_framework.permissions import IsAuthenticated
# 5
from rest_framework.views import APIView


#serializing
# 1 - Typical Jsonresponse
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many = True)
    return JsonResponse({
        'data' : serializer.data
    })

# 2 - fbv Class
@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many = True)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail(request, pk): #get a single_products
    product = get_object_or_404(Product, id=pk)
    serializer = ProductSerializer(product)
    return Response(serializer.data)


# 2 - fbv Class
@api_view(['GET'])
def order_list(request):
    # Old Query wich is heavy enough
    #orders = Order.objects.all()
    # New Optimized Query
    #orders = Order.objects.prefetch_related('items').all()
    orders = Order.objects.prefetch_related('items', 'items__product')
    serializer = OrderSerializer(orders, many = True)
    return Response(serializer.data)


# 3 - Aggregated Response
@api_view(['GET'])
def product_info(request):
    products = Product.objects.all()
    serializer = ProductInfoSerializer({
        'products': products,
        'count': len(products),
        'max_price': products.aggregate(max_price=Max('price'))['max_price']
    })
    return Response(serializer.data)


# 4 - Class Based Views
# 4.1 - Generic Views
class ProductsListAPIView(generics.ListAPIView):
    #queryset = Product.objects.all()
    #in case we nedded to retrieve only available products
    queryset = Product.objects.filter(stock__gt=0)
    serializer_class = ProductSerializer

class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Optional look-up keyword
    #lookup_url_kwarg = 'product_id'

class OrdersListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items', 'items__product')
    serializer_class = OrderSerializer

# 4.3 Get Only Self Orders (per user!)
class UserOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items', 'items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)
    
# 5 - APIViews
class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price']
        })
        return Response(serializer.data)


