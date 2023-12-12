import pytest
from tests.factory.cart_item import CartItemFactory


@pytest.fixture
def cart_item(user2, product):
    cart_item = CartItemFactory(customer=user2, product=product)
    cart_item.id = 1
    cart_item.save()
    return cart_item


@pytest.fixture
def cart_item_unauth(product):
    cart_item = CartItemFactory(product=product)
    return cart_item


@pytest.fixture
def non_empty_cart(user2, cart, products):
    cart_items = []
    for i in range(1, 4):
        cart_item = CartItemFactory(customer=user2, id=i, cart=cart, product=products[i-1])
        cart_items.append(cart_item)
    return cart_items
