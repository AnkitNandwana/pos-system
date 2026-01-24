from django.db import models


class Recommendation(models.Model):
    basket_id = models.CharField(max_length=100)
    source_product_id = models.CharField(max_length=50)
    recommended_product_id = models.CharField(max_length=50)
    recommended_product_name = models.CharField(max_length=200)
    recommended_at = models.DateTimeField(auto_now_add=True)
    was_accepted = models.BooleanField(null=True, blank=True)
    
    class Meta:
        db_table = 'recommendations'
    
    def __str__(self):
        return f"{self.source_product_id} → {self.recommended_product_id} (Basket: {self.basket_id})"
