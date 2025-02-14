import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import chat.routing  # ensure this path is correct

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatProject.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
         URLRouter(
            chat.routing.websocket_urlpatterns
         )
    ),
})
