from django.urls import path
from payments import views
urlpatterns = [
    path('khalti/<uuid:order_id>',views.khalti_payment,name="khalti_payment"),
    path('khalti/verify/<uuid:order_id>',views.verify_khalti_payment,name="verify_khalti_payment"),
    path('khalti/refund/<uuid:order_id>',views.refund_khalti_payment,name="refund_khalti_payment")
]