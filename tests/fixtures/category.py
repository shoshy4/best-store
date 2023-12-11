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
def category(admin):
    category = CategoryFactory()
    return category


@pytest.fixture
def categories(user2):
    categories = []
    for ix in range(4):
        category = CategoryFactory()
        categories.append(category)
    return categories
