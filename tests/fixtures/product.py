import pytest
from tests.factory.product import ProductFactory


@pytest.fixture
def product(category):
    product = ProductFactory()
    product.category.add(category)
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
    for i in range(1, 5):
        product = ProductFactory(price=5*i)
        product.id = i
        product.save()
        product.category.add(categories[i-1])
        product.save()
        products.append(product)
    return products
