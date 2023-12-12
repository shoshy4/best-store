import pytest
from tests.factory.product import ProductFactory


@pytest.fixture
def product(category):
    product = ProductFactory(category=category)
    product.id = 1
    product.save()
    return product


@pytest.fixture
def product_not_categorized():
    product = ProductFactory()
    product.save()
    return product


@pytest.fixture
def products(categories):
    products = []
    for i in range(1, 4):
        product = ProductFactory()
        product.id = i
        product.save()
        product.category.add(categories[i-1])
        product.save()
        products.append(product)
    return products
