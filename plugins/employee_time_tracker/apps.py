from django.apps import AppConfig


class EmployeeTimeTrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.employee_time_tracker'
    label = 'employee_time_tracker'
