from cart_wishlist.models import Cart, Wishlist
from django.http import JsonResponse
from users.services import verify_user,verify_token,role_required
from django.views.decorators.csrf  import csrf_exempt
from products.services import verify_product
from cart_wishlist.services import verify_cart_item
import json
import uuid
from django.db import IntegrityError,transaction
# Create your views here.
@csrf_exempt
@verify_token
@role_required('customer')
def create_cart(request):
    if request.method != "POST":
        return JsonResponse({"error":"Invalid method"},status = 405)
    
    try:
        data = json.loads(request.body)
        user_id = request.user_id
        product_id = data.get('product')
        quantity = int(data.get('quantity', 1))
        price = float(data.get('price', 0))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({"error": "Invalid or missing data"}, status=400)
    
    user = verify_user(user_id=user_id)
    product = verify_product(product_id=product_id)
    with transaction.atomic():
        # Check if item already exists in cart
        cart_item = Cart.objects.filter(user=user, product=product).first()

        if cart_item:
            # Already exists → increase quantity by 1
            cart_item.quantity += 1
            cart_item.price = price * cart_item.quantity
            cart_item.save()
            return JsonResponse({
                'message': 'Product already in cart — quantity increased by 1',
                'cart_id': cart_item.id,
                'new_quantity': cart_item.quantity,
                'total_price': cart_item.price
            }, status=200)
        else:
            # Not in cart → create new cart item
            cart_item = Cart.objects.create(
                user=user,
                product=product,
                quantity=quantity,
                price=price * quantity
            )
            return JsonResponse({
                'message': 'Added to cart successfully',
                'cart_id': cart_item.id,
                'quantity': cart_item.quantity,
                'total_price': cart_item.price
            }, status=201)

@csrf_exempt
@verify_token
@role_required('customer')
def edit_cart(request,cart_id):
    if request.method not in ["PUT","POST"]:
        return JsonResponse({"error":"Invalid method"},status = 405)
    try:
        data = json.loads(request.body)
        user_id = request.user_id
        quantity = data.get('quantity')
        price = data.get('price')
    except json.JSONDecodeError:
        return JsonResponse({"error":"Failed to load json"},status = 400)
    
    cart_item = verify_cart_item(cart_id=cart_id)
    if cart_item.user.id != uuid.UUID(user_id):
        return JsonResponse({'error': 'You are not allowed to edit this cart'}, status=403)
    
    if quantity is None or price is None:
        return JsonResponse({'error': 'Both quantity and price are required'}, status=400)

    cart_item.quantity = quantity
    cart_item.price = price * quantity
    cart_item.save()
    return JsonResponse({'message':'Cart Updated successfully'})

@csrf_exempt
@verify_token
def retrieve_cart(request):
    if request.method != "GET":
        return JsonResponse({"error":"Invalid method"},status = 405)
    user_id = request.user_id
    user = verify_user(user_id=user_id)
    try:
        cart_item = Cart.objects.filter(user = user)
    except Cart.DoesNotExist:
        return JsonResponse({"error": "Cart item not found"}, status=404)
    
    data = []
    for cart in cart_item:
        data.append({
            'id' : str(cart.id),
            'product' : cart.product.name,
            'quantity' : cart.quantity,
            'price': cart.price
        })

    return JsonResponse({'cart item':data})

@csrf_exempt
@verify_token
@role_required('customer')
def delete_cart(request,cart_id):
    if request.method != "DELETE":
        return JsonResponse({"error":"Invalid method"},status = 405)
    
    user_id = request.user_id    
    cart_item = verify_cart_item(cart_id=cart_id)
    if cart_item.user.id != uuid.UUID(user_id):
        return JsonResponse({'error': 'You are not allowed to delete this cart'}, status=403)

    cart_item.delete()
    return JsonResponse({'error':'Cart Item deleted successfully'})

@csrf_exempt
@verify_token
@role_required('customer')
def create_wishlist(request):
    if request.method != "POST":
        return JsonResponse({"error":"Invalid method"},status = 405)
    try:
        data = json.loads(request.body)
        user_id = request.user_id
        product_id = data.get('product')
    except json.JSONDecodeError:
        return JsonResponse({"error":"Failed to load json"},status = 400)
    
    user = verify_user(user_id=user_id)
    product = verify_product(product_id=product_id)

    try:
        wishlist = Wishlist.objects.create(user=user, product=product)
        return JsonResponse({
            'message': 'Added to wishlist successfully',
            'wishlist_id': wishlist.id
        }, status=201)

    except IntegrityError:
        # This happens when (user, product) already exists
        return JsonResponse({
            'message': 'This product is already in your wishlist'
        }, status=200)
    
@csrf_exempt
@verify_token
def retrieve_wishlist(request):
    if request.method != "GET":
        return JsonResponse({"error":"Invalid method"},status = 404)
    user_id = request.user_id
    user = verify_user(user_id=user_id)
    try:
        wishlist_item = Wishlist.objects.filter(user=user)
    except Wishlist.DoesNotExist:
        return JsonResponse({'error':'Wishlist doenot exist'},status = 404)
    
    data = []
    for item in wishlist_item:
        data.append({
            "id" : str(item.id),
            'product' : item.product.name
        })
    return JsonResponse({'Wishlist item':data})
    
    
@csrf_exempt
@verify_token
@role_required('customer')
def delete_wishlist(request,wishlist_id):
    if request.method != "DELETE":
        return JsonResponse({"error":"Invalid method"},status = 404)
    user_id = request.user_id
    try:
        wishlist_item = Wishlist.objects.get(id=wishlist_id)
    except Wishlist.DoesNotExist:
        return JsonResponse({'error':'Wishlist doenot exist'},status = 404)
    if wishlist_item.user.id != uuid.UUID(user_id):
        return JsonResponse({'error': 'You are not allowed to delete this wishlist'}, status=403)
    wishlist_item.delete()
    return JsonResponse({'message':'Wishlist deleted successfully'},status = 404)
    

    

