from django.apps import AppConfig


class CustomerLookupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.customer_lookup'
    label = 'customer_lookup'
