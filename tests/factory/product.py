import factory
import factory.fuzzy
from store_app.models import *

from .category import CategoryFactory


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.fuzzy.FuzzyText()
    description = factory.fuzzy.FuzzyText()
    price = factory.fuzzy.FuzzyDecimal()
    amount_in_stock = factory.fuzzy.FuzzyInteger()
    image = factory.django.ImageField()
    category = factory.SubFactory(CategoryFactory)
