from cart_wishlist.models import Cart, Wishlist
from django.http import JsonResponse
from users.services import verify_user,verify_token,role_required
from django.views.decorators.csrf  import csrf_exempt
from products.services import verify_product
from cart_wishlist.services import verify_cart_item
import json
import uuid
from django.db import IntegrityError,transaction
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from asgiref.sync import async_to_sync
# Create your views here.
@login_required(login_url="users:login")
# @role_required('customer')
def create_cart(request):
    if request.method != "POST":
        return JsonResponse({"error":"Invalid method"},status = 405)
    
    try:
        data = json.loads(request.body)
        user_id = request.user.id
        product_id = data.get('product')
        quantity = int(data.get('quantity', 1))
        price = float(data.get('price', 0))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({"error": "Invalid or missing data"}, status=400)
    
    user = async_to_sync(verify_user)(user_id=user_id)
    if isinstance(user, JsonResponse):
        return user
    product = verify_product(product_id=product_id)
    if isinstance(product, JsonResponse):
        return product
    with transaction.atomic():
        # Check if item already exists in cart
        cart_item = Cart.objects.filter(user=user, product=product).first()

        if cart_item:
            # Already exists → increase quantity by 1
            cart_item.quantity += quantity
            cart_item.price = price * cart_item.quantity
            cart_item.save()
            return JsonResponse({
                'message': f'Product already in cart — quantity increased by {quantity}',
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

@login_required
# @role_required('customer')
def edit_cart(request,cart_id):
    if request.method not in ["PUT","POST"]:
        return JsonResponse({"error":"Invalid method"},status = 405)
    try:
        data = json.loads(request.body)
        user_id = request.user.id
        quantity = int(data.get('quantity'))
        price = float(data.get('price'))
    except json.JSONDecodeError:
        return JsonResponse({"error":"Failed to load json"},status = 400)
    
    cart_item = verify_cart_item(cart_id=cart_id)
    if isinstance(cart_item, JsonResponse):
        return cart_item
    if cart_item.user.id != user_id:
        return JsonResponse({'error': 'You are not allowed to edit this cart'}, status=403)
    
    if quantity is None or price is None:
        return JsonResponse({'error': 'Both quantity and price are required'}, status=400)

    cart_item.quantity = quantity
    cart_item.price = price
    cart_item.save()
    return JsonResponse({'message':'Cart Updated successfully'})

@login_required(login_url="users:login")
def retrieve_cart(request):
    if request.method != "GET":
        return JsonResponse({"error":"Invalid method"},status = 405)
    
    user_id = request.user.id
    user = async_to_sync(verify_user)(user_id=user_id)
    if isinstance(user, JsonResponse):
        return user
    try:
        cart_item = Cart.objects.filter(user = user)
    except Cart.DoesNotExist:
        return JsonResponse({"error": "Cart item not found"}, status=404)
    
    data = []
    total_product_price = 0
    delivery_charge = 150
    for cart in cart_item:
        data.append({
            'id' : str(cart.id),
            'product' : cart.product.name,
            'quantity' : cart.quantity,
            'price': cart.price
        })
        total_product_price += cart.price

    total_price = total_product_price + delivery_charge
    context = {'cart_items': data,
               'total_product_price': total_product_price,
                'delivery': delivery_charge,
                'total_price': total_price
            }
    return render(request, "ecommerce/cart_page.html", context=context)
    # return JsonResponse({'cart item':data})

@login_required(login_url="users:login")
# @role_required('customer')
def delete_cart(request,cart_id):
    if request.method != "DELETE":
        return JsonResponse({"error":"Invalid method"},status = 405)
    
    user_id = request.user.id 
    cart_item = verify_cart_item(cart_id=cart_id)
    if isinstance(cart_item, JsonResponse):
        return cart_item
    if cart_item.user.id != user_id:
        return JsonResponse({'error': 'You are not allowed to delete this cart'}, status=403)

    cart_item.delete()
    return JsonResponse({'message':'Cart Item deleted successfully'})

@login_required(login_url="users:login")
# @role_required('customer')
def create_wishlist(request):
    if request.method != "POST":
        return JsonResponse({"error":"Invalid method"},status = 405)
    try:
        data = json.loads(request.body)
        user_id = request.user.id
        product_id = data.get('product')
    except json.JSONDecodeError:
        return JsonResponse({"error":"Failed to load json"},status = 400)
    
    user = async_to_sync(verify_user)(user_id=user_id)
    if isinstance(user, JsonResponse):
        return user
    product = verify_product(product_id=product_id)
    if isinstance(product, JsonResponse):
        return product

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
    
@login_required(login_url="users:login")
def retrieve_wishlist(request):
    if request.method != "GET":
        return JsonResponse({"error":"Invalid method"},status = 404)
    user_id = request.user.id
    user = async_to_sync(verify_user)(user_id=user_id)
    if isinstance(user, JsonResponse):
        return user
    try:
        wishlist_item = Wishlist.objects.filter(user=user)
    except Wishlist.DoesNotExist:
        return JsonResponse({'error':'Wishlist doenot exist'},status = 404)
    
    data = []
    for item in wishlist_item:
        data.append({
            "id" : str(item.id),
            'product' : item.product.name,
            'price': item.product.price,
            'stock' : item.product.stock
        })
    context = {
        "wishlist_items" : data
    }

    return render(request,"ecommerce/wishlist_page.html",context=context)
    # return JsonResponse({'Wishlist item':data})
    
    
@login_required(login_url="users:login")
# @role_required('customer')
def delete_wishlist(request,wishlist_id):
    if request.method != "DELETE":
        return JsonResponse({"error":"Invalid method"},status = 404)
    user_id = request.user.id
    try:
        wishlist_item = Wishlist.objects.get(id=wishlist_id)
    except Wishlist.DoesNotExist:
        return JsonResponse({'error':'Wishlist doenot exist'},status = 404)
    if wishlist_item.user.id != user_id:
        return JsonResponse({'error': 'You are not allowed to delete this wishlist'}, status=403)
    wishlist_item.delete()
    return JsonResponse({'message':'Wishlist deleted successfully'},status = 404)