from django.contrib import admin
from .models import Terminal


@admin.register(Terminal)
class TerminalAdmin(admin.ModelAdmin):
    list_display = ['terminal_id', 'employee', 'login_time', 'logout_time', 'is_active']
    list_filter = ['is_active', 'login_time']
    search_fields = ['terminal_id', 'employee__username']
    readonly_fields = ['terminal_id', 'login_time']
