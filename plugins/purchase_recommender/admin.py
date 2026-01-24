from django.contrib import admin
from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['basket_id', 'source_product_id', 'recommended_product_id', 'recommended_product_name', 'recommended_at', 'was_accepted']
    list_filter = ['was_accepted', 'recommended_at']
    search_fields = ['basket_id', 'source_product_id', 'recommended_product_id']
    readonly_fields = ['recommended_at']
