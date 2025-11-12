from django.urls import path
from videocall import views
urlpatterns = [
    path("",views.videocallpage,name="videocall_page"),
    path('remove-online-user', views.remove_online_user, name='remove_online_user'),
]