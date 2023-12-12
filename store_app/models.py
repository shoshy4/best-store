from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def validate_above_zero(value):
    if value <= 0:
        raise ValidationError(
            _("%(value)s must be above 0"),
            params={"value": value},
        )


class Category(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    amount_in_stock = models.IntegerField(validators=[validate_above_zero])
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    category = models.ManyToManyField(Category, related_name='product', blank=True, null=True)

    def __str__(self):
        return f"{self.name}: ${self.price}"


class Cart(models.Model):
    OPEN = "O"
    PROCESSED = "P"
    CLOSED = "C"
    STATUS_CHOICES = (
        (OPEN, "Open"),
        (PROCESSED, 'Being processed'),
        (CLOSED, "Closed"),
    )
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, default='O', max_length=1)
    total_price = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    def calculate_total_price(self):
        return CartItem.objects.filter(cart=self).aggregate(Sum('price'))


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    cart = models.ForeignKey(Cart, related_name="cart_items", on_delete=models.CASCADE)

    @property
    def total(self):
        return self.amount*self.product.price


class PaymentDetails(models.Model):
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)
    expiration_date = models.DateField()
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    default = models.BooleanField(default=False, blank=True, null=True)


class ShippingAddress(models.Model):
    street_address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=10)
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    default = models.BooleanField(default=False, blank=True)


class Order(models.Model):
    IN_PROCESS = 1
    NOT_COMPLETED = 2
    PAID = 3
    SENT = 4
    DELIVERED = 5
    RECEIVED = 6
    ORDER_STATUS_CHOICES = (
        (IN_PROCESS, "Completed. Payment in process"),
        (NOT_COMPLETED, "Not completed yet. Make sure payment_details and shipping_address are added"),
        (PAID, "Paid. In process"),
        (SENT, "Sent to customer's shipping address"),
        (DELIVERED, "Delivered"),
        (RECEIVED, "Received")
    )

    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product_list = models.OneToOneField(Cart, related_name="cart", on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    shipping_address = models.ForeignKey(ShippingAddress, related_name='shipping_address', on_delete=models.CASCADE,
                                         blank=True, null=True)
    payment_details = models.ForeignKey(PaymentDetails, on_delete=models.CASCADE, blank=True, null=True)
    order_status = models.IntegerField(choices=ORDER_STATUS_CHOICES, default=NOT_COMPLETED)
    paid = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)

    def calculate_status_for_new_order(self):
        tmp_status = Order.IN_PROCESS
        payment_details = PaymentDetails.objects.filter(default=True)
        shipping_address = ShippingAddress.objects.filter(default=True)
        if not shipping_address or not payment_details:
            tmp_status = Order.NOT_COMPLETED
        if shipping_address:
            shipping_address = shipping_address[0]
        if payment_details:
            payment_details = payment_details[0]
        return tmp_status, payment_details, shipping_address


class Feedback(models.Model):
    RATE_CHOICES = (
        (5, "excellent"),
        (4, "very good"),
        (3, "good"),
        (2, "not bad"),
        (1, "bad"),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='feedback')
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)
    text = models.TextField(blank=True, null=True)
