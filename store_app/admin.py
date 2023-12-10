from django.contrib import admin
from .models import Category, Product, Cart, CartItem, PaymentDetails, ShippingAddress, Order, Feedback

admin.site.register(Category)
admin.site.register(Product)
# Для корзины добавить отображение продуктов.  Добавление inlines, StackedInline
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(PaymentDetails)
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(Feedback)
