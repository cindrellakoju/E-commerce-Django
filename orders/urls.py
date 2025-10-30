from django.urls import  path
from orders import views
urlpatterns = [
    path('create',views.create_order,name="create order"),
    path('edit/<uuid:order_id>',views.edit_order,name="edit order"),
    path('delete/<uuid:order_id>',views.delete_order,name="delete order"),
    path('',views.retrieve_order,name="retrieve Order"),
    path('item/create',views.insert_order_item,name="Insert order item")
]