import factory
import factory.fuzzy
from store_app.models import *
from .user import UserFactory

STATUS_CODES = [x[0] for x in Cart.STATUS_CHOICES]


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    customer = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice(STATUS_CODES)
    total_price = factory.fuzzy.FuzzyDecimal(low=0, high=100000)
