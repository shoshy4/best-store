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
    cart = CartFactory(status=Cart.STATUS_CHOICES.OPEN)
    return cart
