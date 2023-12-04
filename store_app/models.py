from django.contrib import auth
from django.db import models
from django.core.exceptions import ValidationError
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
    category = models.ManyToManyField(Category)

    def __str__(self):
        return self.name


class Cart(models.Model):
    STATUS_CHOICES = (
        ('O', "Open"),
        ('C', "Closed"),
    )
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, default='O', max_length=1)
    total_price = models.DecimalField(max_digits=7, decimal_places=2, default=0)


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
    cart = models.ForeignKey(Cart, related_name="cart_items", on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name


class PaymentDetails(models.Model):
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)
    expiration_date = models.DateField()
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    default = models.BooleanField(default=False, blank=True)


class ShippingAddress(models.Model):
    street_address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=10)
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    default = models.BooleanField(default=False, blank=True)


class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        (1, "Paid. In process"),
        (2, "In process. Please add payment_details"),
        (3, "In process. Please add shipping_address"),
        (4, "In process. Please add payment_details and shipping_address"),
        (5, "Sent to customer's shipping address"),
        (6, "Received")
    )

    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product_list = models.OneToOneField(Cart, related_name="cart", on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=7, decimal_places=2)
    shipping_address = models.ForeignKey(ShippingAddress, related_name='shipping_address', on_delete=models.CASCADE,
                                         blank=True, null=True)
    payment_details = models.ForeignKey(PaymentDetails, on_delete=models.CASCADE, blank=True, null=True)
    order_status = models.IntegerField(choices=ORDER_STATUS_CHOICES, default=1)
    paid = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)


class Feedback(models.Model):
    RATE_CHOICES = (
        (5, "excellent"),
        (4, "very good"),
        (3, "good"),
        (2, "not bad"),
        (1, "bad"),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)
    text = models.TextField(blank=True, null=True)




