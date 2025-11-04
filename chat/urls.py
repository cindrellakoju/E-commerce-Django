from django.urls import path
from . import views

urlpatterns = [
    path("chatroom",views.view_chat,name="chat room")
]
