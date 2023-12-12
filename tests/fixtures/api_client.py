import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client_unauth():
    return APIClient(), None


@pytest.fixture
def api_client_auth(user2):
    client = APIClient()
    client.force_authenticate(user=user2)
    return client, user2


@pytest.fixture
def api_client_user(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def api_client_admin(admin):
    client = APIClient()
    client.force_authenticate(user=admin)
    return client, admin
