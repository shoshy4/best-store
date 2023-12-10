from django_filters import rest_framework as filters
from .models import Product, Order, Category, Cart


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    # TODO: по описанию лучше не надо, слишком затратно
    description = filters.CharFilter(lookup_expr='icontains')
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    price = filters.NumberFilter(field_name="price", lookup_expr='exact')
    category = filters.CharFilter(lookup_expr='icontains', field_name="category__name")

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category']


class OrderFilter(filters.FilterSet):
    order_status = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Order
        fields = ['customer', 'product_list', 'total_price', 'order_status', 'paid']


class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['name']


class CartFilter(filters.FilterSet):
    STATUS_CHOICES = (
        ('0', "Open"),
        #  TODO: Closed отличается от модели
        ('c', "Closed"),
    )
    status = filters.ChoiceFilter(choices=STATUS_CHOICES)
    total_price = filters.NumberFilter(field_name="total_price", lookup_expr='exact')
    customer = filters.CharFilter(lookup_expr='icontains', field_name="customer__username")

    class Meta:
        model = Cart
        fields = ['status', 'total_price', 'customer']
