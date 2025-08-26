from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at", "total_items", "total_price")
    inlines = [CartItemInline]

    def total_items(self, obj):
        return obj.total_items()

    total_items.short_description = "Total Items"

    def total_price(self, obj):
        return obj.total_price()

    total_price.short_description = "Total Price"


class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "subtotal")

    def subtotal(self, obj):
        return obj.subtotal()

    subtotal.short_description = "Subtotal"


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
