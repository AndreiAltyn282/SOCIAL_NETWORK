import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from messages_app.consumers import ChatConsumer  # <-- ИСПРАВЛЕНО!

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_network.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/chat/<int:conversation_id>/', ChatConsumer.as_asgi()),
        ])
    ),
})
