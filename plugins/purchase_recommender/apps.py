from django.apps import AppConfig


class PurchaseRecommenderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.purchase_recommender'
    label = 'purchase_recommender'
