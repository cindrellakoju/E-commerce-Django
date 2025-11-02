# from . import views
# from django.urls import path

# urlpatterns = [
#     path("",views.index,name="index"),
#     path("<int:question_id>/results/", views.results, name="results"),
#     path("signup",views.signup,name="signup"),
#     path("login",views.login_view,name="login"),
#     path("profile/<uuid:user_id>",views.login_user,name="user_profile")
# ]
from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
]
