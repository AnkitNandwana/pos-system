from django.db import models
from django.conf import settings
import uuid


class AgeVerificationState(models.Model):
    basket_id = models.CharField(max_length=100, unique=True)
    requires_verification = models.BooleanField(default=False)
    verification_completed = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verifier_employee_id = models.IntegerField(null=True, blank=True)
    customer_age = models.IntegerField(null=True, blank=True)
    verification_method = models.CharField(max_length=50, null=True, blank=True)
    restricted_items = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'age_verification_states'
    
    def __str__(self):
        return f"{self.basket_id} - {'Verified' if self.verification_completed else 'Pending'}"


class AgeVerificationViolation(models.Model):
    VIOLATION_TYPES = [
        ('UNVERIFIED_RESTRICTED_ITEMS', 'Unverified Restricted Items'),
        ('INSUFFICIENT_AGE', 'Insufficient Age'),
        ('INVALID_VERIFICATION', 'Invalid Verification'),
        ('SYSTEM_ERROR', 'System Error'),
    ]
    
    violation_id = models.UUIDField(default=uuid.uuid4, unique=True)
    basket_id = models.CharField(max_length=100)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    terminal_id = models.CharField(max_length=100, null=True, blank=True)
    violation_type = models.CharField(max_length=50, choices=VIOLATION_TYPES)
    details = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'age_verification_violations'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Violation {self.violation_id} - {self.violation_type}"