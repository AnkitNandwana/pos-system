from django.apps import AppConfig


class FraudDetectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.fraud_detection'
    label = 'fraud_detection'