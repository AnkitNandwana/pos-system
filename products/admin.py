from django.contrib import admin
from .models import Product, RecommendationRule


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'price', 'category', 'created_at']
    search_fields = ['product_id', 'name', 'category']
    list_filter = ['category']


@admin.register(RecommendationRule)
class RecommendationRuleAdmin(admin.ModelAdmin):
    list_display = ['source_product', 'recommended_product', 'priority', 'is_active']
    list_filter = ['is_active']
    search_fields = ['source_product__name', 'recommended_product__name']
