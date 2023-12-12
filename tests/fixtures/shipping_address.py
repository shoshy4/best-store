import pytest
from tests.factory.shipping_address import ShippingAddressFactory


@pytest.fixture
def shipping_address(user2):
    shipping_address = ShippingAddressFactory(customer=user2)
    shipping_address.id = 1
    shipping_address.save()
    return shipping_address


@pytest.fixture
def shipping_address2(user2):
    shipping_address = ShippingAddressFactory(customer=user2)
    shipping_address.id = 2
    shipping_address.save()
    return shipping_address


@pytest.fixture
def shipping_address_unauth():
    shipping_address = ShippingAddressFactory()
    return shipping_address


@pytest.fixture
def few_shipping_address(user2):
    shipping_addresses = []
    shipping_address1 = ShippingAddressFactory(customer=user2)
    shipping_address1.id = 1
    shipping_address1.save()
    shipping_addresses.append(shipping_address1)
    for i in range(2, 4):
        shipping_address = ShippingAddressFactory(customer=user2, id=i, default=True)
        shipping_addresses.append(shipping_address)
    return shipping_addresses
