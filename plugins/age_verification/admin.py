from django.contrib import admin
from .models import AgeVerificationState, AgeVerificationViolation


@admin.register(AgeVerificationState)
class AgeVerificationStateAdmin(admin.ModelAdmin):
    list_display = ['basket_id', 'requires_verification', 'verification_completed', 'verified_at', 'customer_age']
    list_filter = ['requires_verification', 'verification_completed', 'verification_method']
    search_fields = ['basket_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basket Information', {
            'fields': ('basket_id', 'requires_verification', 'restricted_items')
        }),
        ('Verification Details', {
            'fields': ('verification_completed', 'verified_at', 'verifier_employee_id', 'customer_age', 'verification_method')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(AgeVerificationViolation)
class AgeVerificationViolationAdmin(admin.ModelAdmin):
    list_display = ['violation_id', 'basket_id', 'employee', 'violation_type', 'timestamp']
    list_filter = ['violation_type', 'timestamp']
    search_fields = ['basket_id', 'employee__username', 'violation_id']
    readonly_fields = ['violation_id', 'timestamp']
    
    fieldsets = (
        ('Violation Information', {
            'fields': ('violation_id', 'basket_id', 'employee', 'terminal_id', 'violation_type')
        }),
        ('Details', {
            'fields': ('details', 'timestamp')
        })
    )