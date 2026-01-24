from django.contrib import admin
from .models import TimeEntry


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'terminal_id', 'clock_in', 'clock_out', 'total_hours']
    list_filter = ['clock_in', 'employee']
    search_fields = ['employee__username', 'terminal_id']
    readonly_fields = ['total_hours']
