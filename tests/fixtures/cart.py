import pytest
from store_app.models import Cart
from tests.factory.cart import CartFactory


@pytest.fixture
def cart(user2):
    cart = CartFactory(customer=user2, status=Cart.STATUS_CHOICES.OPEN)
    cart.id = 1
    cart.save()
    return cart


@pytest.fixture
def cart_unauth():
    cart = CartFactory()
    return cart


@pytest.fixture
def closed_carts(user2):
    cart1 = CartFactory(customer=user2)
    cart1.id = 4
    cart1.save()
    carts = [cart1]
    for i in range(1, 4):
        cart = CartFactory(customer=user2, id=i, status=Cart.STATUS_CHOICES.CLOSED)
        carts.append(cart)
    return carts
