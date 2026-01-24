from django.db import models


class PluginConfiguration(models.Model):
    name = models.CharField(max_length=100, unique=True)
    enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'plugin_configurations'
    
    def __str__(self):
        return f"{self.name} ({'Enabled' if self.enabled else 'Disabled'})"
