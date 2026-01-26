from django.urls import re_path
from plugins.purchase_recommender import routing as recommendation_routing
from plugins.fraud_detection import routing as fraud_routing
from events.session_consumer import SessionConsumer

websocket_urlpatterns = [
    re_path(r'ws/session/(?P<terminal_id>[\w-]+)/$', SessionConsumer.as_asgi()),
    *recommendation_routing.websocket_urlpatterns,
    *fraud_routing.websocket_urlpatterns,
]