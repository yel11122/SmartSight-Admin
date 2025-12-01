"""
ASGI config for admin_site project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_site.settings')

# 1. Get the standard Django HTTP handler (for all non-WebSocket requests)
django_asgi_app = get_asgi_application()

# 2. Import your app's routing configuration
# IMPORTANT: This assumes your routing file is inside an app named 'admin_panel'
import admin_panel.routing 

# 3. Define the master router that splits traffic by protocol
application = ProtocolTypeRouter({
    # Handles all standard HTTP requests (GET, POST, etc.)
    "http": django_asgi_app, 
    
    # Handles WebSocket connections
    # AuthMiddlewareStack ensures you can access the current user in your Consumer
    "websocket": AuthMiddlewareStack(
        URLRouter(
            admin_panel.routing.websocket_urlpatterns
        )
    ),
})
