import pytest
from tests.factory.feedback import FeedbackFactory


@pytest.fixture
def feedback_unauth(product):
    feedback = FeedbackFactory(product=product)
    return feedback


@pytest.fixture
def feedback_wrong(product, user):
    feedback = FeedbackFactory(product=product, customer=user)
    return feedback


@pytest.fixture
def feedback(product, user2):
    feedback = FeedbackFactory(product=product, customer=user2)
    return feedback


@pytest.fixture
def feedbacks(product, user2):
    feedbacks = []
    for i in range(1, 4):
        feedback = FeedbackFactory(product=product, id=i, customer=user2)
        feedbacks.append(feedback)
    return feedbacks
