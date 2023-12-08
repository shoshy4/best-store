import factory
import factory.fuzzy
from store_app.models import *

from .cart import CartFactory
from .product import ProductFactory


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    product = factory.SubFactory(ProductFactory)
    amount = factory.fuzzy.FuzzyInteger()
    price = factory.fuzzy.FuzzyDecimal()
    cart = factory.SubFactory(CartFactory)
