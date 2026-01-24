from django.db import models
from django.conf import settings
import uuid


class Terminal(models.Model):
    terminal_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='terminals')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'terminals'
        indexes = [
            models.Index(fields=['employee', 'is_active']),
        ]
    
    def __str__(self):
        return f"Terminal {self.terminal_id} - {self.employee.username}"
