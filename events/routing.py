from django.urls import re_path
from plugins.purchase_recommender import routing as recommendation_routing

websocket_urlpatterns = [
    *recommendation_routing.websocket_urlpatterns,
]