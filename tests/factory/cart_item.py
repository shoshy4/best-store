import factory
import factory.fuzzy
from store_app.models import *

from .cart import CartFactory
from .product import ProductFactory


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    product = factory.SubFactory(ProductFactory)
    amount = factory.fuzzy.FuzzyInteger(low=0, high=1000)
    price = factory.fuzzy.FuzzyDecimal(low=0, high=1000)
    cart = factory.SubFactory(CartFactory)
