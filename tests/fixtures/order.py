import pytest
from tests.factory.order import OrderFactory


@pytest.fixture
def order(user2, cart, shipping_address, payment_details):
    order = OrderFactory(customer=user2, product_list=cart, shipping_address=shipping_address,
                         payment_details=payment_details)
    order.id = 1
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
        order = OrderFactory(customer=user2, id=i, product_list=closed_carts[i], shipping_address=shipping_address,
                             payment_details=payment_details)
        orders.append(order)
    return orders