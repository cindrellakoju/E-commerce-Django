from django.urls import re_path
from chat import customers

# Url for websocket
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<user_id>[0-9a-fA-F\-]+)/$', customers.ChatCustomer.as_asgi()),
]