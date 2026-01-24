from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    list_display = ['username', 'employee_id', 'role', 'first_name', 'last_name', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Employee Info', {'fields': ('employee_id', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Employee Info', {'fields': ('employee_id', 'role')}),
    )
