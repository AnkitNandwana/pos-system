from django.db import models
from apps.plugins.models import Plugin

class PluginEventSubscription(models.Model):
    plugin = models.ForeignKey(
        Plugin,
        on_delete=models.CASCADE,
        related_name="event_subscriptions"
    )

    event_name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("plugin", "event_name")
        indexes = [
            models.Index(fields=["event_name", "active"])
        ]

    def __str__(self):
        return f"{self.plugin.name} → {self.event_name}"
