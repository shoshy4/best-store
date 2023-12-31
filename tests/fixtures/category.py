import pytest
from tests.factory.category import CategoryFactory


@pytest.fixture
def category_unauth():
    category = CategoryFactory()
    return category


@pytest.fixture
def category_user(user2):
    category = CategoryFactory()
    return category


@pytest.fixture
def category():
    category = CategoryFactory()
    return category


@pytest.fixture
def category1():
    category = CategoryFactory(id=1)
    return category


@pytest.fixture
def categories():
    categories = []
    for i in range(4):
        category = CategoryFactory()
        category.id = i + 1
        category.save()
        categories.append(category)
    return categories
