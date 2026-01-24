from django.db import models


class Product(models.Model):
    product_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    age_restricted = models.BooleanField(default=False)
    minimum_age = models.IntegerField(null=True, blank=True)
    age_restriction_category = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'products'
    
    def __str__(self):
        return f"{self.name} ({self.product_id})"


class RecommendationRule(models.Model):
    source_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='triggers')
    recommended_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='recommendations')
    priority = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'recommendation_rules'
        unique_together = ['source_product', 'recommended_product']
    
    def __str__(self):
        return f"{self.source_product.product_id} → {self.recommended_product.product_id}"
