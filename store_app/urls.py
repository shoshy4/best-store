from django.conf import settings
from django.conf.urls.static import static

from .views_api import CategoryCreateList, CategoryUpdateDetailRemove, ProductCreateList, ProductUpdateDetailRemove, \
    CartCreateList, CartUpdateDetailRemove, CartItemCreateList, CartItemUpdateDetailRemove, PaymentDetailsCreateList, \
    OrderCreateList, OrderUpdateDetailRemove, OrderChangeStatus, OrderList, PaymentDetailsUpdateDetailRemove, \
    ShippingAddressCreateList, ShippingAddressUpdateDetailRemove, FeedbackCreateList
from django.urls import path


urlpatterns = [
    path('category/', CategoryCreateList.as_view(), name="category_list_create_api"),
    path('category/<int:pk>/', CategoryUpdateDetailRemove.as_view(), name="category_update_detail_remove_api"),
    path('product/', ProductCreateList.as_view(), name="product_list_create_api"),
    path('product/<int:pk>/', ProductUpdateDetailRemove.as_view(), name="product_update_detail_remove_api"),
    path('product/<int:pk>/feedback/', FeedbackCreateList.as_view(), name="feedback_list_create_api"),
    path('product/<int:pk>/feedback/<int:feedback_pk>/', FeedbackCreateList.as_view(),
         name="feedback_update_detail_remove_api"),
    path('orders/', OrderList.as_view(), name="order_list_api"),
    path('cart/', CartItemCreateList.as_view(), name="item_create_list_remove_api"),
    path('cart/items/<int:pk>/', CartItemUpdateDetailRemove.as_view(), name="item_update_detail_remove_api"),
    path('order/', OrderCreateList.as_view(), name="order_list_create_api"),
    path('order/<int:pk>/', OrderUpdateDetailRemove.as_view(), name="order_update_detail_remove_api"),
    path('order/<int:pk>/change_status', OrderChangeStatus.as_view(),
         name="order_change_status_api"),
    path('payment-details/', PaymentDetailsCreateList.as_view(), name="payment_details_list_create_api"),
    path('payment-details/<int:pk>/', PaymentDetailsUpdateDetailRemove.as_view(),
         name="payment_details_update_detail_remove_api"),
    path('shipping-address/', ShippingAddressCreateList.as_view(), name="shipping_address_list_create_api"),
    path('shipping-address/<int:pk>/', ShippingAddressUpdateDetailRemove.as_view(),
         name="shipping_address_update_detail_remove_api"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
