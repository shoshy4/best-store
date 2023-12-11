import pytest
from tests.factory.user import UserFactory


@pytest.fixture
def user():
    user = UserFactory()
    return user


@pytest.fixture
def user2():
    user = UserFactory()
    return user


@pytest.fixture
def admin():
    user = UserFactory(is_staff=True, is_superuser=True)
    return user
