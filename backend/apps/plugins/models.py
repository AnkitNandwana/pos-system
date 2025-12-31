# backend/plugins/models.py
from django.db import models

class Plugin(models.Model):
    EVENT_TYPES = [
        ("EMPLOYEE_LOGIN", "Employee Login"),
        ("EMPLOYEE_LOGOUT", "Employee Logout"),
    ]

    name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict)

    def __str__(self):
        return self.name