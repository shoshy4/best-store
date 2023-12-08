from datetime import datetime

import factory
import factory.fuzzy
from store_app.models import *
from .user import UserFactory
from .product import ProductFactory

RATES = [x[0] for x in Feedback.RATE_CHOICES]


class FeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feedback

    product = factory.SubFactory(ProductFactory)
    customer = factory.SubFactory(UserFactory)
    rate = factory.fuzzy.FuzzyChoice(RATES)
    text = factory.fuzzy.FuzzyText()

