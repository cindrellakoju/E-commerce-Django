from django.urls import re_path
from . import customers

websocket_urlpatterns = [
    re_path(r'ws/signaling/$', customers.WebRTCustomer.as_asgi()),
]
