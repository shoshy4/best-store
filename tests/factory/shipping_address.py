from datetime import datetime
import factory
import factory.fuzzy
from store_app.models import *

from .user import UserFactory


class ShippingAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShippingAddress

    street_address = factory.fuzzy.FuzzyText()
    city = factory.fuzzy.FuzzyText()
    state = factory.fuzzy.FuzzyText()
    zip_code = factory.fuzzy.FuzzyText(length=10)
    customer = factory.SubFactory(UserFactory)
    default = False
