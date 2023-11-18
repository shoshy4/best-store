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
    path('all_orders/', OrderList.as_view(), name="order_list_api"),
    path('items/', CartItemCreateList.as_view(), name="item_create_list_remove_api"),
    path('items/<int:pk>/', CartItemUpdateDetailRemove.as_view(), name="item_update_detail_remove_api"),
    path('cart/', CartCreateList.as_view(), name="cart_list_create_api"),
    path('cart/<int:pk>/', CartUpdateDetailRemove.as_view(), name="cart_update_detail_remove_api"),
    path('cart/<int:pk>/items/', CartItemCreateList.as_view(), name="cart_item_list_create_api"),
    path('cart/<int:pk>/items/<int:items_pk>', CartItemUpdateDetailRemove.as_view(),
         name="cart_item_update_detail_remove_api"),
    path('cart/<int:pk>/order/', OrderCreateList.as_view(), name="order_list_create_api"),
    path('cart/<int:pk>/order/<int:order_pk>/', OrderUpdateDetailRemove.as_view(), name="order_update_detail_remove_api"),
    path('cart/<int:pk>/order/<int:order_pk>/change_status', OrderChangeStatus.as_view(),
         name="order_change_status_api"),
    path('payment-details/', PaymentDetailsCreateList.as_view(), name="payment_details_list_create_api"),
    path('payment-details/<int:pk>/', PaymentDetailsUpdateDetailRemove.as_view(),
         name="payment_details_update_detail_remove_api"),
    path('shipping-address/', ShippingAddressCreateList.as_view(), name="shipping_address_list_create_api"),
    path('shipping-address/<int:pk>/', ShippingAddressUpdateDetailRemove.as_view(),
         name="shipping_address_update_detail_remove_api"),
    # path('items/<int:pk><int:pk>/', CartItemUpdateDetailRemove.as_view(), name="item_update_detail_remove_api"),
    # path('items/', CartItemCreateList.as_view(), name="item_list_create_api"),

    # path('tasks_list/', TasksListCreateList.as_view(), name="tasks_list_list_create_api"),
    # path('tasks_list/<int:pk>/', TasksListUpdateDetailRemove.as_view(),
    #      name="tasks_list_update_detail_remove_api"),
    # path('tasks_list/<int:pk>/task/', TaskCreateList.as_view(), name="task_list_create_grouped_api"),
    # path('tasks_list/<int:pk>/task/<int:task_pk>/', TaskUpdateDetailRemove.as_view(),
    #      name="task_update_detail_remove_grouped_api"),
]
