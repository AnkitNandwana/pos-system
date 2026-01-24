from django.contrib.auth.models import AbstractUser
from django.db import models


class Employee(AbstractUser):
    ROLE_CHOICES = [
        ('CASHIER', 'Cashier'),
        ('MANAGER', 'Manager'),
        ('ADMIN', 'Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CASHIER')
    employee_id = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'employees'
    
    def __str__(self):
        return f"{self.username} ({self.role})"
