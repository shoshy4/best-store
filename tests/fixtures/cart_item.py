import pytest
from tests.factory.cart_item import CartItemFactory


@pytest.fixture
def cart_item(product, cart):
    cart_item = CartItemFactory(product=product, cart=cart)
    cart_item.id = 1
    cart_item.save()
    return cart_item


@pytest.fixture
def cart_filled_items(cart_filled, products):
    cart_items = []
    for product in products:
        cart_item = CartItemFactory(cart=cart_filled, product=product)
        cart_items.append(cart_item)
    return cart_items


@pytest.fixture
def non_empty_cart(cart, products):
    cart_items = []
    for i in range(1, 5):
        cart_item = CartItemFactory(id=i, cart=cart, product=products[i - 1])
        cart_items.append(cart_item)
    return cart_items


