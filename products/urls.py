from django.urls import path
from products import views
urlpatterns = [
    path("category/create",views.create_category,name="create category"),
    path("category/edit/<slug:slug>",views.edit_category,name="edit category"),
    path('category',views.retrieve_category,name="retrieve category"),
    path("category/delete/<slug:slug>",views.delete_category,name="delete category"),
    path('create',views.create_product,name='create product'),
    path('edit/<slug:slug>',views.edit_product,name='edit product'),
    path('delete/<slug:slug>',views.delete_product,name='delete product'),
    path('',views.retrieve_product,name='retrieve product'),
    path('image/add',views.add_image,name='add image'),
    path('image/delete/<uuid:image_id>',views.delete_image,name='delete image'),
    path('search',views.search_engine,name="search product")
]