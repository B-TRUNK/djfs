from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        #fields = '__all__'
        fields = ('id', 'name', 'description', 'price', 'stock')


        def validate_price(self, value):
            if value <= 0:
                raise serializers.ValidationError("Price Must be Greater than Zero")
            return value

