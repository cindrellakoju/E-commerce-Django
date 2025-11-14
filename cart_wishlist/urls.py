from django.urls import path
from cart_wishlist import views
urlpatterns = [
    path('cart/create',views.create_cart,name="create_cart"),
    path('cart/edit/<uuid:cart_id>',views.edit_cart,name="edit_cart"),
    path('cart/delete/<uuid:cart_id>',views.delete_cart,name="delete_cart"),
    path('cart',views.retrieve_cart,name="retrieve_cart"),
    path('wishlist/create',views.create_wishlist,name="create_wishlist"),
    path('wishlist/delete/<uuid:wishlist_id>',views.delete_wishlist,name="delete_wishlist"),
    path('wishlist',views.retrieve_wishlist,name="retrieve_wishlist"),
]