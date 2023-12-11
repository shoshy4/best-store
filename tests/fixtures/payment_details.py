import pytest
from tests.factory.payment_details import PaymentDetailsFactory


@pytest.fixture
def payment_details(user2):
    payment_details = PaymentDetailsFactory(customer=user2)
    payment_details.id = 1
    payment_details.save()
    return payment_details


@pytest.fixture
def payment_details_unauth():
    payment_details = PaymentDetailsFactory()
    return payment_details


@pytest.fixture
def few_payment_details(user2):
    payment_details = []
    payment1 = PaymentDetailsFactory(customer=user2)
    payment1.id = 1
    payment1.save()
    payment_details.append(payment1)
    for i in range(2, 4):
        payment = PaymentDetailsFactory(customer=user2, id=i, default=True)
        payment_details.append(payment)
    return payment_details
