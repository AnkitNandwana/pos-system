from django.contrib import admin
from .models import Customer, CustomerLookupLog


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'tier', 'loyalty_points', 'total_purchases']
    search_fields = ['customer_id', 'identifier', 'first_name', 'last_name', 'email', 'phone']
    list_filter = ['tier', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CustomerLookupLog)
class CustomerLookupLogAdmin(admin.ModelAdmin):
    list_display = ['customer_identifier', 'basket_id', 'status', 'duration_ms', 'request_timestamp']
    list_filter = ['status', 'request_timestamp']
    search_fields = ['customer_identifier', 'basket_id']
    readonly_fields = ['request_timestamp', 'response_timestamp']
