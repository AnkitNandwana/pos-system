from django.db import models
from django.conf import settings
import uuid


class FraudRule(models.Model):
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    rule_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    time_window = models.IntegerField(help_text="Time window in seconds")
    threshold = models.IntegerField()
    enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fraud_rules'
    
    def __str__(self):
        return f"{self.name} ({self.severity})"


class FraudAlert(models.Model):
    alert_id = models.UUIDField(default=uuid.uuid4, unique=True)
    rule = models.ForeignKey(FraudRule, on_delete=models.CASCADE)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    terminal_id = models.CharField(max_length=100, null=True, blank=True)
    basket_id = models.CharField(max_length=100, null=True, blank=True)
    severity = models.CharField(max_length=10)
    details = models.JSONField()
    acknowledged = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'fraud_alerts'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Alert {self.alert_id} - {self.rule.name}"