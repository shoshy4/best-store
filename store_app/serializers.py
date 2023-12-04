from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Count, Q
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Category, Product, Cart, CartItem, PaymentDetails, ShippingAddress, Order, Feedback


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


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, use_url=True)
    rate_count_dict = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'amount_in_stock', 'image', 'category', 'rate_count_dict']

    def get_rate_count_dict(self, obj):
        return Feedback.objects.filter(product_id=obj.id).values('rate').annotate(rate_count=Count('rate'))


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['name', 'products']

    def get_products(self, obj):
        products = obj.product_set.all()
        response = ProductSerializer(products, many=True).data
        return response


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['amount', 'product']


class CartSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    cart_items = CartItemSerializer(many=True)
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Cart
        fields = ['customer', "cart_items", 'status', 'total_price']


class PaymentDetailsSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    expiration_date = serializers.DateTimeField()

    class Meta:
        model = PaymentDetails
        fields = ['card_number', 'cvv', 'expiration_date', 'customer']


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['street_address', 'city', 'state', 'zip_code', 'customer']


class PaymentSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    paid = serializers.BooleanField(read_only=True, source='payment.paid')

    class Meta:
        model = PaymentDetails
        fields = ['amount', 'description', 'customer', 'paid']


class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    product_list = CartSerializer(read_only=True)
    order_status = serializers.CharField(source='get_order_status_display', read_only=True)
    total_price = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True, source='order.total_price')
    paid = serializers.BooleanField(read_only=True, source='order.paid')

    class Meta:
        model = Order
        fields = ['customer', 'product_list', 'total_price', 'shipping_address', 'payment_details',
                  'order_status', 'paid']


class OrderAdminSerializer(serializers.ModelSerializer):
    product_list = CartSerializer()
    customer = UserSerializer()
    order_status = serializers.CharField(source='get_order_status_display')

    class Meta:
        model = Order
        fields = ['customer', 'product_list', 'total_price', 'shipping_address', 'payment_details',
                  'order_status', 'paid']


class FeedbackSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = ['product', 'customer', 'text', 'rate']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.username
        return token
