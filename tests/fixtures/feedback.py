import pytest
from tests.factory.feedback import FeedbackFactory


@pytest.fixture
def feedback_unauth(product):
    feedback = FeedbackFactory(product=product)
    return feedback


@pytest.fixture
def feedback(user2, product):
    feedback = FeedbackFactory(product=product, customer=user2)
    return feedback
