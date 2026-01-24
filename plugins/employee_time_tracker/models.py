from django.db import models
from django.conf import settings


class TimeEntry(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='time_entries')
    terminal_id = models.CharField(max_length=100)
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'time_entries'
        ordering = ['-clock_in']
    
    def __str__(self):
        return f"{self.employee.username} - {self.clock_in}"
    
    def calculate_hours(self):
        """Calculate total hours worked"""
        if self.clock_out:
            delta = self.clock_out - self.clock_in
            self.total_hours = round(delta.total_seconds() / 3600, 2)
            self.save()
