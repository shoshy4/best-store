import pytest
from tests.factory.product import ProductFactory


@pytest.fixture
def product(category):
    product = ProductFactory(category=category)
    product.id = 1
    product.save()
    return product


@pytest.fixture
def products_category1(category1):
    product1 = ProductFactory(category=category1, id=1)
    product2 = ProductFactory(category=category1, id=2)
    products = [product1, product2]
    return products


@pytest.fixture
def product_not_categorized():
    product = ProductFactory()
    return product


@pytest.fixture
def products(categories):
    products = []
    for i in range(1, 4):
        product = ProductFactory(category=categories[i-1], id=i)
        products.append(product)
    return products
