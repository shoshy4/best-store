import pytest
from tests.factory.product import ProductFactory


@pytest.fixture
def product(category, user2):
    product = ProductFactory(category=category)
    product.id = 1
    product.save()
    return product


@pytest.fixture
def product_not_categorized():
    product = ProductFactory()
    return product
