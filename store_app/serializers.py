from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Category, Product, Cart, CartItem, PaymentDetails, ShippingAddress, Order, Feedback


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Category
        fields = ['name']


class CartSerializer(serializers.ModelSerializer):
    customer = serializers.ReadOnlyField(source='cart.customer')

    class Meta:
        model = Cart
        fields = ['customer']


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'amount_in_stock', 'image', 'categories']


class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ['name', 'amount', 'product', 'cart']


class PaymentDetailsSerializer(serializers.ModelSerializer):
    customer = serializers.ReadOnlyField(source='payment-details.customer')

    class Meta:
        model = PaymentDetails
        fields = ['card_number', 'cvv', 'expiration_date', 'amount', 'customer']


class ShippingAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShippingAddress
        fields = ['street_address', 'city', 'state', 'zip_code']


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.ReadOnlyField(source='order.customer')

    class Meta:
        model = Order
        fields = ['customer', 'product_list', 'total_price', 'shipping_address', 'payment_details',
                  'order_status', 'paid']


class FeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Feedback
        fields = ['product', 'customer', 'text']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.username
        return token


class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data.get('username'),
            password=make_password(validated_data.get('password'))
        )

        user.set_password(validated_data['password'])
        validated_data.pop('confirm_password')  # added
        user.save()
        return user
