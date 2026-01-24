from django.db import models


class Customer(models.Model):
    TIER_CHOICES = [
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
    ]
    
    customer_id = models.CharField(max_length=50, unique=True)
    identifier = models.CharField(max_length=100, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    loyalty_points = models.IntegerField(default=0)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='BRONZE')
    total_purchases = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_purchase_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer_id})"


class CustomerLookupLog(models.Model):
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('TIMEOUT', 'Timeout'),
    ]
    
    basket_id = models.CharField(max_length=100)
    customer_identifier = models.CharField(max_length=100)
    api_endpoint = models.URLField()
    request_timestamp = models.DateTimeField(auto_now_add=True)
    response_timestamp = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    response_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'customer_lookup_logs'
    
    def __str__(self):
        return f"{self.customer_identifier} - {self.status}"
