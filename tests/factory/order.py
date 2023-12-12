from datetime import datetime
import factory
import factory.fuzzy
from store_app.models import *
from .user import UserFactory
from .cart import CartFactory
from .payment_details import PaymentDetailsFactory
from .shipping_address import ShippingAddressFactory

STATUS_CODES = [x[0] for x in Order.ORDER_STATUS_CHOICES]


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    customer = factory.SubFactory(UserFactory)
    product_list = factory.SubFactory(CartFactory)
    total_price = factory.fuzzy.FuzzyDecimal(low=0, high=100000)
    shipping_address = factory.SubFactory(ShippingAddressFactory)
    payment_details = factory.SubFactory(PaymentDetailsFactory)
    order_status = factory.fuzzy.FuzzyChoice(STATUS_CODES)
    paid = False
    created_date = factory.fuzzy.FuzzyDate(datetime.now().date())

