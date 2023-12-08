import factory
import factory.fuzzy
from store_app.models import *


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.fuzzy.FuzzyText()