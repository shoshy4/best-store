from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
#from .filters import TaskFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category, Product, Cart, CartItem, PaymentDetails, ShippingAddress, Order, Feedback
from .permissions import IsAdminPermission
from .serializers import CategorySerializer, ProductSerializer, CartSerializer, CartItemSerializer, \
    PaymentDetailsSerializer, ShippingAddressSerializer, OrderSerializer, FeedbackSerializer, UserSerializer
from rest_framework import generics


class CategoryCreateList(generics.ListCreateAPIView):
    permission_classes = [IsAdminPermission]
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = Category.objects.all()


class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
