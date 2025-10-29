from django.http import JsonResponse
from cart_wishlist.models import Cart

def verify_cart_item(cart_id):
    try:
        cart_item = Cart.objects.get(id=cart_id)
    except Cart.DoesNotExist:
        return JsonResponse({"error": "Cart item not found"}, status=404)
    return cart_item