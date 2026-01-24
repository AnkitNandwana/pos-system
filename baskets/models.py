from django.db import models
from employees.models import Employee


class Basket(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('FINALIZED', 'Finalized'),
        ('PAID', 'Paid'),
    ]
    
    basket_id = models.CharField(max_length=100, unique=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='baskets')
    customer_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'baskets'
    
    def __str__(self):
        return f"{self.basket_id} - {self.status}"


class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='items')
    product_id = models.CharField(max_length=50)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'basket_items'
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
