from django.contrib import admin
from .models import FraudRule, FraudAlert


@admin.register(FraudRule)
class FraudRuleAdmin(admin.ModelAdmin):
    list_display = ['rule_id', 'name', 'severity', 'threshold', 'time_window', 'enabled']
    list_filter = ['severity', 'enabled']
    search_fields = ['rule_id', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FraudAlert)
class FraudAlertAdmin(admin.ModelAdmin):
    list_display = ['alert_id', 'rule', 'employee', 'severity', 'timestamp']
    list_filter = ['severity', 'timestamp', 'rule']
    search_fields = ['alert_id', 'employee__username']
    readonly_fields = ['alert_id', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False