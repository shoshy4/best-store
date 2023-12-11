from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Count
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Category, Product, Cart, CartItem, PaymentDetails, ShippingAddress, Order, Feedback
from rest_framework import serializers


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

     # TODO: Можно добавить валидацию username, что такого имени больше нет - Q
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
    # rate_count_dict = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'amount_in_stock', 'image', 'category', 'rate_count']

    # TODO: Могут быть проблемы с производительностью,
    #  добавляем в prefetch или поле для подсчета среднего рейтинга в модель -DONE
    # def get_rate_count_dict(self, obj):
    #     return Feedback.objects.filter(product_id=obj.id).values('rate').annotate(rate_count=Count('rate'))


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    # TODO: Можно напрямую указать сериализатор, без SerializerMethodField - DONE
    products = ProductSerializer()

    class Meta:
        model = Category
        fields = ['name', 'products']

    def get_products(self, obj):
        products = obj.product_set.all()
        response = ProductSerializer(products, many=True).data
        return response


class CartItemSerializer(serializers.ModelSerializer):
    # price = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)

    def validate(self, data):
        product = get_object_or_404(Product, pk=data["product"])
        if product.amount_in_stock < data["amount"]:
            raise serializers.ValidationError("You are trying to add more than exists of this product")
        if product.amount_in_stock == 0:
            raise serializers.ValidationError("This product: %s is out of stock" % product.name)
        return data

    class Meta:
        model = CartItem
        fields = ['amount', 'product', 'total']


class CartSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    cart_items = CartItemSerializer(many=True)
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Cart
        fields = ['customer', "cart_items", 'status', 'total_price']


class PaymentDetailsSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    expiration_date = serializers.DateField()

    class Meta:
        model = PaymentDetails
        fields = ['card_number', 'cvv', 'expiration_date', 'customer', 'default']


class ShippingAddressSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)

    class Meta:
        model = ShippingAddress
        fields = ['street_address', 'city', 'state', 'zip_code', 'customer', 'default']


class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    product_list = CartSerializer(read_only=True)
    order_status = serializers.CharField(source='get_order_status_display', read_only=True)
    total_price = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True, source='order.total_price')
    paid = serializers.BooleanField(read_only=True, source='order.paid')
    created_date = serializers.DateTimeField(format="%m/%d/%Y %H:%M")

    class Meta:
        model = Order
        fields = ['customer', 'product_list', 'total_price', 'shipping_address', 'payment_details',
                  'order_status', 'paid', 'created_date']


class OrderAdminSerializer(serializers.ModelSerializer):
    product_list = CartSerializer()
    customer = UserSerializer()
    order_status = serializers.CharField(source='get_order_status_display')
    created_date = serializers.DateTimeField(format="%m/%d/%Y %H:%M")

    class Meta:
        model = Order
        fields = ['customer', 'product_list', 'total_price', 'shipping_address', 'payment_details',
                  'order_status', 'paid', 'created_date']


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
