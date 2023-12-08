from datetime import datetime
import factory
import factory.fuzzy
from store_app.models import *

from .user import UserFactory


class PaymentDetailsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PaymentDetails

    card_number = factory.fuzzy.FuzzyText(length=16)
    cvv = factory.fuzzy.FuzzyText(length=3)
    expiration_date = factory.fuzzy.FuzzyDate(datetime.now().date())
    customer = factory.SubFactory(UserFactory)
    default = False
