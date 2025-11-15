from rest_framework import serializers
from .models import Product, Order, OrderItem
from django.db import transaction


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'description',
            'name',
            'price',
            'stock',
        )

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0."
            )
        return value
    

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source='product.price')

    class Meta:
        model = OrderItem
        fields = (
            'product_name',
            'product_price',
            'quantity',
            'item_subtotal'
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='total')
    order_id = serializers.UUIDField(read_only=True)

    def total(self, obj):
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items)

    class Meta:
        model = Order
        fields = (
            'order_id',
            'created_at',
            'user',
            'status',
            'items',
            'total_price',
        )

# Working with Aggregated Data
class ProductInfoSerializer(serializers.Serializer):
    # get all products, count of products, max price
    products = ProductSerializer(many=True)
    count    = serializers.IntegerField()
    max_price = serializers.FloatField() 


# Advanced Serialization
"""
when submitting a POST for orders, we get a respone of empty 
feedback [], note the following so our mission is to fill the gap

{
  "order_id": "ea55e71b-9f6c-437d-809d-7deb39894231",
  "created_at": "2025-11-14T22:40:21.210896Z",
  "user": 1,
  "status": "Confirmed",
  "items": [],
  "total_price": 0
}
* Notice the nested serializer below
* even after this serializer selection decision is added to the 'orders' viewset
you will still get:
*AssertionError: The `.create()` method does not support writable nested fields by default.
*Write an explicit `.create()` method for serializer `fsapp.serializers.OrderCreateSerializer`,
*or set `read_only=True` on nested serializer fields."""

class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ['product', 'quantity']
    
    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemCreateSerializer(many=True, required=False)

    #Explicit create def
    def create(self, validated_data):
        orderitem_data = validated_data.pop('items') 

        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for item in orderitem_data:
                OrderItem.objects.create(order=order, **item)

        return order
    

    #Explicit update def
    def update(self,instance, validated_data):
        orderitem_data = validated_data.pop('items')

        with transaction.atomic():
            instance = super().update(instance, validated_data)

        if orderitem_data is not None:
            # Clear Existing items (optional, depends on requirements)
            instance.items.all().delete()

            # Recreate the items with the Updated Data
            for item in orderitem_data:
                OrderItem.objects.create(order=instance, **item)

        return instance


    class Meta:
        model = Order
        fields = (
            'order_id',
            'user',
            'status',
            'items',
        )
        #in order to inject the userId to feedback response as a read only field
        extra_kwargs = {
            'user': {'read_only': True}
        }

