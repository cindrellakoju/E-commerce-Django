from . import views
from django.urls import path

urlpatterns = [
    path("",views.index,name="index"),
    path("<int:question_id>/results/", views.results, name="results"),
    path("signup",views.signup,name="signup"),
    path("login",views.login_view,name="login")
]