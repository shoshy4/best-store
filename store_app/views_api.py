import decimal
import json

from django.contrib.auth.models import User
from django.core import serializers
from django.db.models import Prefetch, Count
from django.http import JsonResponse
from django_filters import rest_framework as filters
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .filters import ProductFilter, OrderFilter, CategoryFilter, CartFilter
from .models import Category, Product, Cart, CartItem, PaymentDetails, ShippingAddress, Order, Feedback
from .permissions import IsAdminPermission, IsOwnerOrAdminPermission
from .serializers import CategorySerializer, ProductSerializer, CartSerializer, CartItemSerializer, \
    PaymentDetailsSerializer, ShippingAddressSerializer, OrderSerializer, FeedbackSerializer, UserSerializer, \
    OrderAdminSerializer
from rest_framework import generics, status


class CategoryCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAdminPermission]
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CategoryFilter
    queryset = Category.objects.all()


class CategoryUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminPermission]
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    queryset = Category.objects.all()


class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProductCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAdminPermission]
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter
    queryset = Product.objects.prefetch_related('category').all()


class OrderList(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OrderAdminSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = OrderFilter
    queryset = Order.objects.prefetch_related('product_list').prefetch_related('customer').prefetch_related(
        'shipping_address') \
        .prefetch_related('payment_details').all()


class ProductUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminPermission]
    serializer_class = ProductSerializer
    queryset = Product.objects.prefetch_related('category').all()


class CartItemCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CartItemSerializer
        return CartSerializer

    def get_queryset(self):
        cart = Cart.objects.filter(customer=self.request.user, status='O').filter(status='P')
        return cart.prefetch_related(
            Prefetch('cart_items',
                     queryset=CartItem.objects.select_related('product'),
                     to_attr='item'))

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        cart = Cart.objects.filter(status="O").filter(status='P')
        if not cart:
            # create a new Cart with the new data from response
            cart = Cart.objects.create(customer=self.request.user)
        else:
            cart = cart[0]
        product = get_object_or_404(Product, pk=data["product"])
        if product.amount_in_stock == 0:
            headers = self.get_success_headers(serializer.data)
            return Response({'Message': 'This product is out of stock'},
                            status=status.HTTP_400_BAD_REQUEST, headers=headers)
        if product.amount_in_stock < data["amount"]:
            headers = self.get_success_headers(serializer.data)
            return Response({'Message': 'You are trying to add more than exists of this product'},
                            status=status.HTTP_400_BAD_REQUEST, headers=headers)
        price = decimal.Decimal(self.request.data["amount"]) * product.price
        cart.total_price += price
        cart.save()
        if cart.status == 'P':
            order = Order.pbjects.filter(product_list_id=cart.id)
            order.update(total_price=cart.total_price)
        # perform_create method
        serializer.save(cart=cart, price=price)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CartItemUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return CartItem.objects.filter(cart__customer=self.request.user, cart__status="O")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        product = get_object_or_404(Product, pk=instance.product)
        if product.amount_in_stock < self.request.data["amount"]:
            headers = self.get_success_headers(serializer.data)
            return Response({'Message': 'You are trying to add more than exists of this product'},
                            status=status.HTTP_400_BAD_REQUEST, headers=headers)
        cart = Cart.objects.filter(id=instance.product_list.id)
        old_price = instance.price
        instance.price = decimal.Decimal(self.request.data["amount"]) * product.price
        instance.save()
        total_price = cart[0].total_price - old_price + instance.price
        cart.update(total_price=total_price)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        cart = Cart.objects.filter(status="O").filter(status="P")
        self.perform_destroy(instance)
        cart_items = CartItem.objects.filter(cart__customer=self.request.user).filter(cart=cart)
        if not cart_items:
            cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCreateList(generics.ListCreateAPIView):
    permission_classes = [IsOwnerOrAdminPermission]
    serializer_class = OrderSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_date')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        open_cart = Cart.objects.filter(status='O')
        if not open_cart:
            headers = self.get_success_headers(serializer.data)
            return Response({'Message': 'No cart found with status Open'},
                            status=status.HTTP_404_NOT_FOUND, headers=headers)
        cart = Cart.objects.filter(id=open_cart[0].id)
        cart.update(status='P')
        tmp_status = 1
        flag = False
        payment_details = PaymentDetails.objects.filter(default=True)
        shipping_address = ShippingAddress.objects.filter(default=True)
        if not shipping_address:
            tmp_status = 3
            flag = True
            shipping_address = None
        else:
            shipping_address = shipping_address[0]
        if not payment_details:
            payment_details = None
            if flag:
                tmp_status = 4
            else:
                tmp_status = 2
        else:
            payment_details = payment_details[0]
        total_price = cart[0].total_price
        serializer.save(product_list=cart[0], customer=self.request.user, total_price=total_price,
                        order_status=tmp_status, payment_details=payment_details,
                        shipping_address=shipping_address)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdminPermission]

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return OrderAdminSerializer
        return OrderSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        flag = False
        tmp_status = instance.order_status
        price = instance.total_price
        # if shipping address is being added
        if (instance.order_status == 3 or instance.order_status == 4) \
                and ((self.request.data.get("shipping_address") is not None)
                     and not self.request.data.get("shipping_address") == ""):
            if instance.order_status == 4:
                tmp_status = 2
                flag = True
            else:
                tmp_status = 1
        # if payment_details is being added
        if (instance.order_status == 2 or instance.order_status == 4) \
                and ((self.request.data.get("payment_details")
                      is not None) and not self.request.data.get("payment_details") == ""):
            if flag:
                tmp_status = 1
            else:
                tmp_status = 3
        # if nor shipping_address nor payment_details are not being added
        if (instance.order_status == 4) and (self.request.data.get("payment_details") is None
                                             or (self.request.data.get("payment_details") == "")
                                             and (self.request.data.get("shipping_address") is None
                                                  or (self.request.data.get("shipping_address") == ""))):
            tmp_status = 5
        # update total_price of updated product_list (cart)
        if (self.request.data.get("product_list")) is not None and not (self.request.data.get("product_list") == ""):
            cart = get_object_or_404(Cart, self.request.data.get("product_list"))
            price = cart.total_price
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        # update product_list's (cart) total_price when total_price is being updated
        if self.request.user.is_staff:
            if (self.request.data.get("total_price")) is not None and not (self.request.data.get("total_price") == ""):
                cart = Cart.objects.filter(id=instance.product_list.id)
                price = self.request.data.get("total_price")
                cart.update(total_price=price)
        serializer.is_valid(raise_exception=True)
        serializer.save(order_status=tmp_status, total_price=price)
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

    def perform_update(self, serializer):
        serializer.save(order_status=7)


class PaymentDetailsCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentDetailsSerializer

    def get_queryset(self):
        return PaymentDetails.objects.filter(customer=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data
        payment_details = PaymentDetails.objects.filter(default=True, customer=self.request.user)
        default_value = False
        if not payment_details:
            default_value = True
        elif payment_details[0].default and "default" in data and data["default"]:
            payment_details.update(default=False)
            default_value = True
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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        if "default" in data:
            default_value = data["default"]
            if default_value:
                PaymentDetails.objects.all(customer=self.request.user).update(default=False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
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

    def create(self, request, *args, **kwargs):
        data = request.data
        shipping_address = ShippingAddress.objects.filter(default=True, customer=self.request.user)
        default_value = False
        if not shipping_address:
            default_value = True
        elif shipping_address[0].default and data["default"]:
            shipping_address.update(default=False)
            default_value = True
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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        if "default" in data:
            default_value = data["default"]
            if default_value:
                ShippingAddress.objects.all(customer=self.request.user).update(default=False)
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        paid_orders = Order.objects.filter(customer=self.request.user, paid=True)
        for order in paid_orders:
            cart = get_object_or_404(Cart, pk=order.product_list_id)
            if cart.cart_item_set.all().filter(id=request.data.get(id)).exists():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                headers = self.get_success_headers(serializer.data)
                return Response({'Message': 'You cannot leave a feedback for this product, first purchase it please'},
                                status=status.HTTP_400_BAD_REQUEST, headers=headers)


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
        return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(id=self.kwargs.get('pk')).prefetch_related('product_list').prefetch_related(
                        'customer').prefetch_related('shipping_address').prefetch_related('payment_details')

    def post(self, request, *args, **kwargs):
        order = self.get_queryset()
        products = Product.objects.all()
        cart = get_object_or_404(Cart, pk=order[0].product_list)
        cart_items = cart.prefetch_related(
            Prefetch('cart_items',
                     queryset=CartItem.objects.select_related('product'),
                     to_attr='item'))
        for item in cart_items:
            product = products.filter(id=item.product_id)
            if product.amount_in_stock < item.amount:
                return Response({'Message': 'Amount in stock of this product has been changed \
                - You are trying to take more than exists. Please update the amount and try checkout again.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if product.amount_in_stock == 0:
                return Response({'Message': 'This product is out of stock'},
                                status=status.HTTP_400_BAD_REQUEST)
            amount_in_stock = product.amount_in_stock-item.amount
            product.update(amount_in_stock=amount_in_stock)
        response = [
            {
                "Message": "Your payment has been processed successfully. Your order has been confirmed",
                "Order_number": order[0].id,
            },
            {"Order information":
                {
                    serializers.serialize('json', order)
                }
            }
        ]
        order.update(order_status=1, paid=True)
        return Response(response, status=status.HTTP_200_OK)
