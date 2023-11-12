from django.contrib import auth
from django.db import models


class Category(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    amount_in_stock = models.IntegerField()
    image = models.ImageField()
    admin = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.name


class Cart(models.Model):
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)


class CartItem(models.Model):
    name = models.TextField()
    amount = models.FloatField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart,  on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PaymentDetails(models.Model):
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)
    expiration_date = models.DateTimeField()
    amount = models.IntegerField()
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)


class ShippingAddress(models.Model):
    street_address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)


class Order(models.Model):
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product_list = models.OneToOneField(Cart, primary_key=True, on_delete=models.CASCADE)
    total_price = models.FloatField()
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE)
    payment_details = models.ForeignKey(PaymentDetails, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=50)
    paid = models.BooleanField(default=False)


class Feedback(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    text = models.TextField()






