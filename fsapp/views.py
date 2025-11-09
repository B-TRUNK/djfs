from fsapp.serializers import *
from fsapp.models import *
from django.shortcuts import get_object_or_404
#1
from django.http import JsonResponse
#2
from rest_framework.response import Response
from rest_framework.decorators import api_view

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
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many = True)
    return Response(serializer.data)


