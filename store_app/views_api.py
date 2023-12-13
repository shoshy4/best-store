from decimal import Decimal

from django.contrib.auth.models import User
from django.core import serializers
from django.db.models import Prefetch, Q, Avg, Sum, Count
from django.forms import model_to_dict
from django_filters import rest_framework as filters
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .filters import ProductFilter, OrderFilter, CategoryFilter
from .models import Category, Product, Cart, CartItem, PaymentDetails, ShippingAddress, Order, Feedback
from .permissions import IsAdminPermission, IsOwnerOrAdminPermission
from .serializers import CategorySerializer, ProductSerializer, CartSerializer, CartItemSerializer, \
    PaymentDetailsSerializer, ShippingAddressSerializer, OrderSerializer, FeedbackSerializer, UserSerializer, \
    OrderAdminSerializer
from rest_framework import generics, status

IN_PROCESS = 1
NOT_COMPLETED = 2
PAID = 3
SENT = 4
DELIVERED = 5
RECEIVED = 6


class CategoryCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAdminPermission]
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CategoryFilter
    queryset = Category.objects.all().prefetch_related('product')


class CategoryUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminPermission]
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    queryset = Category.objects.all().prefetch_related('product')


class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProductCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAdminPermission]
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter

    def get_queryset(self):
        products = Product.objects.prefetch_related('category')
        products_with_rating = (products.prefetch_related('feedback').annotate(feedback_rate=Avg('feedback__rate')))
        return products_with_rating


class OrderList(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OrderAdminSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = OrderFilter
    queryset = Order.objects.prefetch_related('product_list').select_related('customer').prefetch_related(
        'shipping_address') \
        .prefetch_related('payment_details').all()


class ProductUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminPermission]
    serializer_class = ProductSerializer
    queryset = Product.objects.prefetch_related('category') \
        # .prefetch_related(
    # Prefetch('feedback',
    #          queryset=Feedback.objects.aggregate(
    #              Avg('feedback__rate'),
    #              to_attr='name')))


class CartItemCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CartItemSerializer
        return CartSerializer

    def get_queryset(self):
        cart = Cart.objects.filter((Q(status=Cart.OPEN) |
                                             Q(status=Cart.PROCESSED)), customer=self.request.user)
        return cart.prefetch_related(
            Prefetch('cart_items',
                     queryset=CartItem.objects.select_related('product'),
                     to_attr='item'))

    def create(self, request, *args, **kwargs):
        data = request.data
        product = get_object_or_404(Product, pk=data["product"])
        price = data["amount"] * product.price
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        cart = Cart.objects.filter(customer=self.request.user).filter(Q(status=Cart.OPEN) |
                                                                      Q(status=Cart.PROCESSED))
        if not cart:
            # create a new Cart with the new data from response
            cart = Cart.objects.create(customer=self.request.user)
        else:
            cart = cart[0]
        cart.total_price += price
        cart.save()
        # perform_create method
        serializer.save(cart=cart, price=price)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CartItemUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return CartItem.objects.filter(cart__customer=self.request.user, cart__status=Cart.OPEN)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if "amount" in request.data:
            instance.cart.total_price -= instance.price
            request.data["price"] = request.data["amount"] * instance.product.price
            instance.cart.total_price += request.data["price"]
            instance.price = request.data["amount"] * instance.product.price
            instance.cart.save()
            instance.save()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        cart = instance.cart
        cart.total_price -= instance.price
        cart.save()
        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCreateList(generics.ListCreateAPIView):
    permission_classes = [IsOwnerOrAdminPermission]
    serializer_class = OrderSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_date')

    def total_price_calculation(self, cart):
        p = CartItem.objects.filter(cart=cart).aggregate(sum=Sum('price'))
        cart.total_price = p['sum']
        cart.save()
        return p['sum']

    def calculate_status_for_new_order(self):
        tmp_status = Order.IN_PROCESS
        payment_details = PaymentDetails.objects.filter(default=True)
        shipping_address = ShippingAddress.objects.filter(default=True)
        if not shipping_address or not payment_details:
            tmp_status = Order.NOT_COMPLETED
        if shipping_address:
            shipping_address = shipping_address[0]
        if payment_details:
            payment_details = payment_details[0]
        return tmp_status, payment_details, shipping_address

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        open_cart = Cart.objects.filter(customer=self.request.user, status=Cart.OPEN)
        if not open_cart:
            headers = self.get_success_headers(serializer.data)
            return Response({'Message': 'No cart found with status Open'},
                            status=status.HTTP_400_BAD_REQUEST, headers=headers)
        cart = open_cart[0]
        cart.status = Cart.PROCESSED
        total_price = self.total_price_calculation(cart)
        cart.save()
        tmp_status, payment_details, shipping_address = self.calculate_status_for_new_order()
        serializer.save(product_list=cart, customer=self.request.user,
                        order_status=tmp_status, payment_details=payment_details,
                        shipping_address=shipping_address, total_price=total_price)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdminPermission]

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return OrderAdminSerializer
        return OrderSerializer

    def calculate_new_status(self, instance):
        tmp_status = instance.order_status
        # if shipping address is being added
        if instance.order_status == Order.NOT_COMPLETED:
            if ((self.request.data.get("shipping_address") is not None
                 and not self.request.data.get("shipping_address") == "") or instance.shipping_address) \
                    and ((self.request.data.get("payment_details") is not None
                          and not self.request.data.get("payment_details") == "") or instance.payment_details):
                tmp_status = Order.IN_PROCESS
        return tmp_status

    def total_price_calculation(self):
        if (self.request.data.get("product_list")) is not None and not (self.request.data.get("product_list") == ""):
            cart = get_object_or_404(Cart, self.request.data.get("product_list"))
            cart.total_price = CartItem.objects.filter(cart=cart).aggregate(Sum('price'))
            cart.save()
            return cart.total_price
        return None

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        tmp_status = self.calculate_new_status(instance)
        total_price = self.total_price_calculation()
        if total_price is None:
            total_price = instance.total_price
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(order_status=tmp_status, total_price=total_price)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def get_queryset(self):
        return Order.objects.filter(id=self.kwargs.get('pk'))


class OrderChangeStatus(generics.UpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OrderAdminSerializer
    queryset = Order.objects.all()


class OrderReceiving(generics.UpdateAPIView):
    permission_classes = [IsOwnerOrAdminPermission]
    serializer_class = OrderAdminSerializer

    def get_queryset(self):
        return Order.objects.filter(id=self.kwargs.get('pk'))

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {"order_status": Order.RECEIVED}
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)


class PaymentDetailsCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentDetailsSerializer

    def get_queryset(self):
        return PaymentDetails.objects.filter(customer=self.request.user)

    def calculate_default(self, data):
        payment_details = PaymentDetails.objects.filter(default=True, customer=self.request.user)
        default_value = False
        if not payment_details:
            default_value = True
        elif payment_details[0].default and self.request.data.get("default") is not None and data["default"]:
            payment_details.update(default=False)
            default_value = True
        return default_value

    def create(self, request, *args, **kwargs):
        data = request.data
        default_value = self.calculate_default(data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=self.request.user, default=default_value)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PaymentDetailsUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdminPermission]
    serializer_class = PaymentDetailsSerializer

    def get_queryset(self):
        return PaymentDetails.objects.filter(customer=self.request.user)

    def update_default(self, data):
        if self.request.data.get("default") is not None:
            default_value = data["default"]
            if default_value:
                PaymentDetails.objects.all(customer=self.request.user).update(default=False)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        self.update_default(data)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.default:
            PaymentDetails.objects.filter(customer=self.request.user).last().update(default=True)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShippingAddressCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShippingAddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(customer=self.request.user)

    def calculate_default(self, data):
        shipping_address = ShippingAddress.objects.filter(default=True, customer=self.request.user)
        default_value = False
        if not shipping_address:
            default_value = True
        elif shipping_address[0].default and data["default"]:
            shipping_address.update(default=False)
            default_value = True
        return default_value

    def create(self, request, *args, **kwargs):
        data = request.data
        default_value = self.calculate_default(data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=self.request.user, default=default_value)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ShippingAddressUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdminPermission]
    serializer_class = ShippingAddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(customer=self.request.user)

    def update_default(self, data):
        if "default" in data:
            default_value = data["default"]
            if default_value:
                PaymentDetails.objects.all(customer=self.request.user).update(default=False)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        self.update_default(data)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.default:
            ShippingAddress.objects.filter(customer=self.request.user).last().update(default=True)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FeedbackCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        return Feedback.objects.filter(product_id=self.kwargs.get('pk'))

    def perform_create(self, serializer):
        product = get_object_or_404(Product, pk=self.kwargs.get('pk'))
        serializer.save(customer=self.request.user, product=product)

    def check_if_paid_for_product(self, serializer, data):
        paid_orders = Order.objects.filter(customer=self.request.user, paid=True)
        for order in paid_orders:
            cart_items = CartItem.objects.filter(cart=order.product_list)
            cart = Cart.objects.prefetch_related('cart_items').filter(id=order.product_list_id)
            if cart_items.all().filter(product_id=self.kwargs.get('pk')).exists():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        headers = self.get_success_headers(serializer.data)
        return Response({'Message': 'You cannot leave a feedback for this product, first purchase it please'},
                        status=status.HTTP_400_BAD_REQUEST, headers=headers)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.check_if_paid_for_product(serializer, data=request.data)


class FeedbackUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdminPermission]
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs.get('feedback_pk'))
        self.check_object_permissions(self.request, obj)
        return obj


class OrderPayment(generics.CreateAPIView):
    permission_classes = [IsOwnerOrAdminPermission]

    def get_serializer_class(self):
        return CartItemSerializer

    def get_queryset(self):
        return Order.objects.filter(id=self.kwargs.get('pk'))

    # .prefetch_related('product_list').prefetch_related(
    #             'customer').prefetch_related('shipping_address').prefetch_related('payment_details')

    def calculate_amount_in_stock(self, order):
        cart = Cart.objects.filter(id=order.product_list.id)
        if not cart[0].status == Cart.PROCESSED:
            raise APIException("Wrong cart status")
        cart.update(status=Cart.CLOSED)
        items = CartItem.objects.filter(cart=cart[0]).select_related('product').all()
        for item in items:
            cart_item_serializer = self.get_serializer(data={"amount": item.amount, "product": item.product_id},
                                                       context={'id': id})
            cart_item_serializer.is_valid(raise_exception=True)
            item.product.amount_in_stock -= item.amount
            item.product.save()

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        self.calculate_amount_in_stock(order)
        response = [
            {
                "Message": "Your payment has been processed successfully. Your order has been confirmed",
                "Order_number": order.id,
            },
            {
                "Order information":
                    {
                        "customer": {
                            "name": order.customer.username
                        },
                        "product_list":
                            {
                                "cart_items": {
                                    order.product_list.cart_items.values().filter(cart=order.product_list)
                                }

                            },
                        "shipping_address": model_to_dict(order.shipping_address),
                        "payment_details": model_to_dict(order.payment_details),
                        "total_price": order.total_price,
                        "order_status": order.get_order_status_display(),
                        "created_date": order.created_date
                    }
            }
        ]
        order.order_status = PAID
        order.paid = True
        order.save()
        return Response(response, status=status.HTTP_200_OK)
