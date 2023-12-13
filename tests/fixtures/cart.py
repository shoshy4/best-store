import pytest
from store_app.models import Cart
from tests.factory.cart import CartFactory


@pytest.fixture
def cart(user2):
    cart = CartFactory(customer=user2, status=Cart.OPEN)
    cart.id = 7
    print(cart)
    cart.save()
    return cart


@pytest.fixture
def cart_filled(user2):
    cart = CartFactory(customer=user2, status=Cart.PROCESSED, total_price=80)
    cart.id = 7
    print(cart)
    cart.save()
    return cart


@pytest.fixture
def cart_unauth():
    cart = CartFactory()
    return cart


@pytest.fixture
def closed_carts(user2):
    cart1 = CartFactory(customer=user2)
    cart1.id = 1
    cart1.save()
    carts = [cart1]
    for i in range(2, 5):
        cart = CartFactory(customer=user2, id=i, status=Cart.CLOSED)
        carts.append(cart)
    return carts
