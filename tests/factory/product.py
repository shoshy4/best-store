import factory
import factory.fuzzy
from store_app.models import *

from .category import CategoryFactory


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.fuzzy.FuzzyText()
    description = factory.fuzzy.FuzzyText()
    price = factory.fuzzy.FuzzyDecimal(low=0, high=1000)
    amount_in_stock = factory.fuzzy.FuzzyInteger(low=0, high=100000)
    image = factory.django.ImageField()
    # category = factory.SubFactory(CategoryFactory)
