from django.contrib import admin
from .models import Category, Product, Cart, CartItem, PaymentDetails, ShippingAddress, Order, Feedback

admin.site.register(Category)
admin.site.register(Product)
# Для корзины добавить отображение продуктов.  Добавление inlines, StackedInline - DONE


class ItemInline(admin.StackedInline):
    model = CartItem
    extra = 1


class CartAdmin(admin.ModelAdmin):
    inlines = [ItemInline]
    list_display = ["customer", "total_price", "status"]


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
admin.site.register(PaymentDetails)
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(Feedback)
