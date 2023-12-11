from django_filters import rest_framework as filters
from .models import Product, Order, Category, Cart


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    # TODO: по описанию лучше не надо, слишком затратно - DONE
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    price = filters.NumberFilter(field_name="price", lookup_expr='exact')
    category = filters.CharFilter(lookup_expr='icontains', field_name="category__name")

    class Meta:
        model = Product
        fields = ['name', 'price', 'category']


class OrderFilter(filters.FilterSet):
    IN_PROCESS = 1
    NOT_COMPLETED = 2
    PAID = 3
    SENT = 4
    DELIVERED = 5
    RECEIVED = 6
    ORDER_STATUS_CHOICES = (
        (IN_PROCESS, "Completed. Payment in process"),
        (NOT_COMPLETED, "Not completed yet. Make sure payment_details and shipping_address are added"),
        (PAID, "Paid. In process"),
        (SENT, "Sent to customer's shipping address"),
        (DELIVERED, "Delivered"),
        (RECEIVED, "Received")
    )
    order_status = filters.ChoiceFilter(choices=ORDER_STATUS_CHOICES)

    class Meta:
        model = Order
        fields = ['customer', 'product_list', 'order_status', 'paid']


class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['name']


class CartFilter(filters.FilterSet):
    STATUS_CHOICES = (
        ('0', "Open"),
        ('P', 'Being processed'),
        #  TODO: Closed отличается от модели - DONE
        ('C', "Closed"),
    )
    status = filters.ChoiceFilter(choices=STATUS_CHOICES)
    # total_price = filters.NumberFilter(field_name="total_price", lookup_expr='exact')
    customer = filters.CharFilter(lookup_expr='icontains', field_name="customer__username")

    class Meta:
        model = Cart
        fields = ['status', 'customer']
