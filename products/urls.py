from django.urls import path
from products import views
urlpatterns = [
    path("category/create",views.create_category,name="create category"),
    path("category/edit/<slug:slug>",views.edit_category,name="edit category"),
    path('category',views.retrieve_category,name="retrieve category"),
    path("category/delete/<slug:slug>",views.delete_category,name="delete category")
]