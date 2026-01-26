from django.urls import re_path
from .consumers import FraudAlertConsumer

websocket_urlpatterns = [
    re_path(r'ws/fraud-alerts/(?P<terminal_id>[\w-]+)/$', FraudAlertConsumer.as_asgi()),
]