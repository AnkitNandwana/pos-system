from django.apps import AppConfig


class PurchaseRecommenderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.purchase_recommender'
    label = 'purchase_recommender'
    
    def ready(self):
        from plugins.registry import plugin_registry
        from .plugin import PurchaseRecommenderPlugin
        plugin_registry.register(PurchaseRecommenderPlugin)
