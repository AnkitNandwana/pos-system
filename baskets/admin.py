from django.contrib import admin
from .models import Basket, BasketItem


class BasketItemInline(admin.TabularInline):
    model = BasketItem
    extra = 0
    readonly_fields = ['added_at']


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ['basket_id', 'employee', 'customer_id', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['basket_id', 'customer_id', 'employee__username']
    inlines = [BasketItemInline]


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    list_display = ['basket', 'product_id', 'product_name', 'quantity', 'price', 'added_at']
    list_filter = ['added_at']
    search_fields = ['product_id', 'product_name', 'basket__basket_id']
