import pytest

from store_app.models import Cart, Order
from tests.factory.order import OrderFactory


@pytest.fixture
def order(user2, cart, shipping_address, payment_details):
    order = OrderFactory(customer=user2, product_list=cart, shipping_address=shipping_address,
                         payment_details=payment_details)
    order.id = 1
    order.save()
    return order


@pytest.fixture
def order_processed(user2, cart_filled_items, shipping_address, payment_details):
    cart_filled = cart_filled_items[0].cart
    order = OrderFactory(customer=user2, product_list=cart_filled, shipping_address=shipping_address,
                         payment_details=payment_details, order_status=Order.IN_PROCESS)
    order.id = 1
    order.save()
    return order


@pytest.fixture
def order_paid(user2, cart_filled_items, shipping_address, payment_details):
    cart_filled = cart_filled_items[0].cart
    order = OrderFactory(customer=user2, product_list=cart_filled, shipping_address=shipping_address,
                         payment_details=payment_details, order_status=Order.PAID)
    order.paid = True
    cart_filled.status = Cart.CLOSED
    cart_filled.save()
    order.save()
    return order


@pytest.fixture
def order_unauth(cart, shipping_address, payment_details):
    order = OrderFactory(product_list=cart, shipping_address=shipping_address,
                         payment_details=payment_details)
    order.id = 1
    order.save()
    return order


@pytest.fixture
def orders(user2, closed_carts, shipping_address, payment_details):
    orders = []
    for i in range(1, 5):
        order = OrderFactory(customer=user2, id=i, product_list=closed_carts[i - 1], shipping_address=shipping_address,
                             payment_details=payment_details)
        orders.append(order)
    return orders
