from orders.models import Orders
from django.http import JsonResponse

def verify_order(order_id):
    try:
        order = Orders.objects.get(id=order_id)
    except Orders.DoesNotExist:
        return JsonResponse({'error':'Product not found'},status = 404)
    return order