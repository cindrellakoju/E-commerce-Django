from django.urls import path
from products import views

app_name = "products"

urlpatterns = [
    path("category/create",views.create_category,name="create category"),
    path("category/edit/<slug:slug>",views.edit_category,name="edit category"),
    path('category',views.retrieve_category,name="retrieve category"),
    path("category/delete/<slug:slug>",views.delete_category,name="delete category"),
    path('create/api',views.create_product,name='create_product'),
    path('create/', views.create_product_page, name='create_product_page'),
    path('edit/<slug:slug>',views.edit_product,name='edit product'),
    path('delete/<slug:slug>',views.delete_product,name='delete product'),
    path('',views.retrieve_product,name='retrieve product'),
    path('image/add',views.add_image,name='add image'),
    path('image/delete/<uuid:image_id>',views.delete_image,name='delete image'),
    path('search',views.search_engine,name="search product"),
    path('review/create',views.create_product_review,name='create product review'),
    path('review/edit/<uuid:review_id>',views.edit_product_review,name='edit product review'),
    path('review/delete/<uuid:review_id>',views.delete_product_review,name='delete product review'),
    path('review/<uuid:product_id>',views.retrieve_product_review,name='retrieve product review'),
]