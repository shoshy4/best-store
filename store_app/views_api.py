import decimal

from django.contrib.auth.models import User
from django.db.models import Prefetch, Count
from django_filters import rest_framework as filters
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .filters import ProductFilter, OrderFilter, CategoryFilter, CartFilter
from .models import Category, Product, Cart, CartItem, PaymentDetails, ShippingAddress, Order, Feedback
from .permissions import IsAdminPermission, IsOwnerOrAdminPermission, IsOwnerOfCartOrAdminPermission
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


class CartCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CartSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CartFilter
    queryset = Cart.objects.prefetch_related('cart_items').all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class CartUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CartSerializer
    pagination_class = PageNumberPagination
    queryset = Cart.objects.filter()


class CartItemCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CartItemSerializer
        return CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user, status="O").prefetch_related(
            Prefetch('cart_items',
                     queryset=CartItem.objects.select_related('product'),
                     to_attr='item'))

    def create(self, request, *args, **kwargs):
        data = request.data
        cart = Cart.objects.filter(status="O")
        if not cart:
            # create a new Cart with the new data from response
            cart = Cart.objects.create(customer=self.request.user)
        else:
            cart = cart[0]
        product = get_object_or_404(Product, pk=data["product"])
        cart.total_price += decimal.Decimal(self.request.data["amount"]) * product.price
        cart.save()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        # perform_create method
        serializer.save(cart=cart)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CartItemUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return CartItem.objects.filter(cart__customer=self.request.user).filter(cart__status="O")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        cart = Cart.objects.filter(status="O")
        cart_items = CartItem.objects.filter(cart__customer=self.request.user).filter(cart=cart)
        if not cart_items:
            cart.delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCreateList(generics.ListCreateAPIView):
    permission_classes = [IsOwnerOfCartOrAdminPermission]
    serializer_class = OrderSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_date')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = Cart.objects.filter(status="O")
        if not cart:
            headers = self.get_success_headers(serializer.data)
            return Response({'Message': 'No cart found with status Open'},
                            status=status.HTTP_404_NOT_FOUND, headers=headers)
        # # remove below line - no longer needed
        # cart = cart.prefetch_related(
        #     Prefetch('cart_items', queryset=CartItem.objects.select_related('product'),
        #              to_attr='item'))
        cart.update(status='C')
        tmp_status = 1
        payment_details = PaymentDetails.objects.filter(default=True)
        shipping_address = ShippingAddress.objects.filter(defaut=True)
        if not shipping_address:
            tmp_status = 3
        if not payment_details:
            tmp_status = 2
        total_price = cart[0].total_price
        serializer.save(product_list=cart[0], customer=self.request.user, total_price=total_price,
                        order_status=tmp_status, payment_details=payment_details[0],
                        shipping_address=shipping_address[0])
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOfCartOrAdminPermission]

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return OrderAdminSerializer
        return OrderSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if ("shipping_address" in instance.order_status) and ((self.request.data.get("shipping_address"))
                                                              or not (self.request.data.get("shipping_address") == "")):
            instance.order_status.replace(". Please add shipping_address", ".")
            instance.save()
        if ("payment_details" in instance.order_status) and ((self.request.data.get("payment_details")) or not
        (self.request.data.get("payment_details") == "")):
            instance.order_status = instance.order_status.replace(". Please add payment_details", ".")
            instance.save()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)


class OrderChangeStatus(generics.UpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OrderAdminSerializer
    queryset = Order.objects.all()


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
        elif payment_details[0].default and data["default"]:
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
    permission_classes = [IsAdminPermission]
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


class FeedbackCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAdminPermission]
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        rate_count_dict = Feedback.objects.values('rate').annotate(rate_count=Count('rate'))
        return Feedback.objects.filter(product_id=self.kwargs.get('pk'))


class FeedbackUpdateDetailRemove(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdminPermission]
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        return Feedback.objects.filter(product_id=self.kwargs.get('pk'), customer=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs.get('feedback_pk'))
