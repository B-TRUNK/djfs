from fsapp.serializers import *
from fsapp.models import *
from django.shortcuts import get_object_or_404
#1
from django.http import JsonResponse
#2
from rest_framework.response import Response
from rest_framework.decorators import api_view
#3
from fsapp.serializers import ProductInfoSerializer, OrderCreateSerializer
from django.db.models import Max
#4
from rest_framework import generics
# Authentication
from rest_framework.permissions import (AllowAny, IsAuthenticated, IsAdminUser)
# 5
from rest_framework.views import APIView
# Backend Filter
from fsapp.filters import ProductFilter, InStockCustomFilterBackend, OrderFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
#Applying Pagination
from fsapp.pagination import LargeResultsSetPagination
#6
from rest_framework import viewsets
from rest_framework.decorators import action
#7 -  Caching
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
#8 - Local Throttle identification
from rest_framework.throttling import ScopedRateThrottle

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

# class OrdersListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related('items', 'items__product')
#     serializer_class = OrderSerializer


# 4.3 Get Only Self Orders (per user!)
# class UserOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related('items', 'items__product')
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         qs = super().get_queryset()
#         return qs.filter(user=self.request.user)
    
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
    

# Create a POST APIView
class ProductListCreateAPIView(generics.ListCreateAPIView):
    throttle_scope = 'products' #gloabally in settings.py
    throttle_classes = [ScopedRateThrottle] #locally and specifically
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockCustomFilterBackend,
        ]
    search_fields   = ['name', 'description']
    ordering_fields = ['name', 'price', 'stock']
    pagination_class = LargeResultsSetPagination
    pagination_class.page_size = 4

    #Caching
    @method_decorator(cache_page(60 * 15 ,key_prefix='product_list'))

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        time.sleep(2)
        return super().get_queryset()


    def get_permissions(self):
        self.permission_classes = [AllowAny]
        #if self.request.method == 'POST':
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    

class ProductUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# 6 - Viewsets
class OrderViewSet(viewsets.ModelViewSet):
    throttle_scope = 'orders'
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]
    #query_for -> ?created_at_lt__2024-11-11

    #Caching
    @method_decorator(cache_page(60 * 15 ,key_prefix='order_list'))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    """
    we have an issue here as when a user is authenticated with his own access
    and another user is logging with his own access key later, the earlier 
    results will be cached to the second user! so we will rely on Authorization key
    and another decorator according to the DRF Documentation (cache_page)
    """
    #user only retrieve/update/delete their own orders, admins have full access
    def get_queryset(self):
        qs =  super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs
    
    # below def is to decide wich serializer to use when creating order
    def get_serializer_class(self):
        # you can also use -> if self.request.method == 'POST':
        if self.action == 'create' or self.action == 'update':
            return OrderCreateSerializer
        return super().get_serializer_class()
    
    """to inject additional fields to the request (user ID as an example when POST)
        then add:
        extra_kwargs = {
            'user': {'read_only': True}
        }
        to the end of the meta class of the serializer
    """
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    # @action(detail=False, methods=['get'], url_path='user-orders')
    # def user_orders(self, request):
    #     orders = self.get_queryset().filter(user=request.user)
    #     serializer = self.get_serializer(orders, many=True)
    #     return Response(serializer.data)

