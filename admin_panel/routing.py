# admin_site/routing.py

from django.urls import re_path

# Import the Consumer class
from . import consumers

# Defines the list of URL patterns for WebSockets
# The master asgi.py file uses this list to route WebSocket traffic
websocket_urlpatterns = [
    # re_path is used here to allow more flexible regex matching, but url patterns work too.
    # The 'StatusConsumer' will handle all connections made to the 'ws/status/' path.
    re_path(r'ws/status/$', consumers.StatusConsumer.as_asgi()),
]
