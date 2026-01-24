from django.apps import AppConfig


class AgeVerificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.age_verification'
    verbose_name = 'Age Verification Plugin'