from django.urls import re_path
from chat import customers

websocket_urlpatterns = [
    re_path(r'ws/group/(?P<group_name>\w+)/$', customers.ChatCustomer.as_asgi()),
]
