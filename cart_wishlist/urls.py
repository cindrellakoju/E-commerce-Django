from django.urls import path
from cart_wishlist import views
urlpatterns = [
    path('cart/create',views.create_cart,name="create_cart"),
    path('cart/edit/<uuid:cart_id>',views.edit_cart,name="edit_cart"),
    path('cart/delete/<uuid:cart_id>',views.delete_cart,name="delete_cart"),
    path('cart',views.retrieve_cart,name="retrieve cart"),
    path('wishlist/create',views.create_wishlist,name="create wishlist"),
    path('wishlist/delete/<uuid:wishlist_id>',views.delete_wishlist,name="delete wishlist"),
    path('wishlist',views.retrieve_wishlist,name="retrieve wishlist"),
]