from django.db import models


class Recommendation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    
    basket_id = models.CharField(max_length=100)
    source_product_id = models.CharField(max_length=50)
    recommended_product_id = models.CharField(max_length=50)
    recommended_product_name = models.CharField(max_length=200)
    recommended_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    reason = models.CharField(max_length=200, default='Frequently bought together', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', null=True, blank=True)
    recommended_at = models.DateTimeField(auto_now_add=True)
    was_accepted = models.BooleanField(null=True, blank=True)
    
    class Meta:
        db_table = 'recommendations'
    
    def save(self, *args, **kwargs):
        # Ensure defaults are set
        if not self.reason:
            self.reason = 'Frequently bought together'
        if not self.status:
            self.status = 'PENDING'
        if self.recommended_price is None:
            self.recommended_price = 0
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.source_product_id} → {self.recommended_product_id} (Basket: {self.basket_id})"
