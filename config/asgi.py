import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

# Import after Django setup
from strawberry.channels import GraphQLWSConsumer
from schema import schema
import events.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path("graphql/", GraphQLWSConsumer.as_asgi(schema=schema)),
                *events.routing.websocket_urlpatterns,
            ])
        )
    ),
})
