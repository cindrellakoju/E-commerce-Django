from django.urls import re_path
from . import customers

websocket_urlpatterns = [
    # Example WebSocket URL for signaling
    # ws://localhost:8000/ws/signaling/
    re_path(r'ws/signaling/(?P<user_id>[0-9a-fA-F\-]+)/$', customers.WebRTCustomer.as_asgi()),
    # re_path(r'ws/signaling/$', customers.WebRTCConsumer.as_asgi()),
]

# from django.urls import re_path
# from . import customers

# websocket_urlpatterns = [
#     # Example WebSocket URL for signaling
#     # ws://localhost:8000/ws/signaling/
# ]
