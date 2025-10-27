from django.urls import path
from products import views
urlpatterns = [
    path("category/create",views.create_category,name="create category")
]