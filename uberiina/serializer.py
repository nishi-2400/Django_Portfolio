from rest_framework import serializers
from .models import Restaurant, Meal, Customer, Driver, Order, OrderDetails


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'phone', 'address', 'logo')


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ('id', 'name', 'short_description', 'image', 'price')


class OrderCustomerSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='user.get_full_name')
    class Meta:
        model = Customer
        fields = ('id', 'name', 'avatar', 'phone', 'address')


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('user', 'avatar', 'phone', 'address')


class OrderDriverSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='user.get_full_name')

    class Meta:
        model = Customer
        fields = ('id', 'name', 'avatar', 'phone', 'address')


class OrderRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'phone', 'address')


class OrderMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ('id', 'name', 'price')


class OrderDetailsSerializer(serializers.ModelSerializer):
    meal = OrderMealSerializer
    class Meta:
        model = OrderDetails
        fields = ('id', 'meal', 'quantity', 'sub_total')
        

class OrderSerializer(serializers.ModelSerializer):
    customer = OrderCustomerSerializer()
    driver = OrderDriverSerializer()
    restaurant = OrderRestaurantSerializer()
    order_details = OrderDetailsSerializer(many=True)
    status = serializers.ReadOnlyField(source="get_status_display")

    class Meta:
        model = Order
        fields = ('id', 'customer', 'restaurant', 'driver', 'order_details', 'total', 'status', 'address')


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ('user', 'avatar', 'phone', 'address', 'location')
