from products.services import verify_product
from django.http import JsonResponse
import json
from orders.models import Orders,OrderItem
from orders.services import verify_order
from users.services import verify_user,verify_token,role_required
import uuid
from django.views.decorators.csrf  import csrf_exempt
from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from asgiref.sync import async_to_sync
from django_redis import get_redis_connection

r = get_redis_connection("default")
# Create your views here.
@csrf_exempt
@login_required
# @role_required('customer') 
def create_order(request):
    if request.method != "POST":
        return JsonResponse({'error':'Invalid method'},status = 405)
    
    user_id = request.user.id
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error':'Failed to decode JSON'},status = 400)
    
    # Required fields
    required_fields = ['total_amount', 'payment_method']
    for field in required_fields:
        if not data.get(field):
            return JsonResponse({'error': f'{field} is required'}, status=400)

    total_amount = Decimal(str(data.get('total_amount', 0)))
    delivery_charge = Decimal(str(data.get('delivery_charge', 110)))
    payment_method = data.get('payment_method')
    payment_status = data.get('payment_status', 'pending')
    order_status = data.get('order_status', 'pending')

    user = async_to_sync(verify_user)(user_id=user_id)
    order = Orders.objects.create(
        user = user,
        total_amount = total_amount,
        delivery_charge = delivery_charge,
        payment_method = payment_method,
        payment_status = payment_status,
        order_status = order_status
    )

    return JsonResponse({'message':'Order created successfully','order_id':order.id},status = 201)

@csrf_exempt
@verify_token
@role_required('customer', 'admin')
def edit_order(request, order_id):
    if request.method not in ["PUT", "PATCH"]:
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        order_status = data.get("order_status")
        payment_status = data.get("payment_status")
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Failed to decode JSON'}, status=400)

    user_id = request.user_id
    role = request.role
    order = verify_order(order_id=order_id)
    if isinstance(order, JsonResponse):
        return order

    if order.user.id != uuid.UUID(user_id) and role != 'admin':
        return JsonResponse({'error': 'You are not allowed to edit this order'}, status=403)

    # Get allowed choices directly from model
    valid_order_statuses = [choice[0] for choice in Orders.ORDER_STATUS_CHOICES]
    valid_payment_statuses = [choice[0] for choice in Orders.PAYMENT_STATUS_CHOICES]

    # Validate order_status
    if order_status and order_status not in valid_order_statuses:
        return JsonResponse({'error': f'Invalid order_status: {order_status}. Must be one of {valid_order_statuses}'}, status=400)

    # Validate payment_status
    if payment_status and payment_status not in valid_payment_statuses:
        return JsonResponse({'error': f'Invalid payment_status: {payment_status}. Must be one of {valid_payment_statuses}'}, status=400)

    # Apply updates
    if order_status:
        if order_status == 'canceled':
            order.order_status = order_status
            order.payment_status = 'canceled' if order.payment_method == 'cod' else 'refunded'
            # NEed to add logic for refund after adding admin or seller
        else:
            order.order_status = order_status

    if payment_status and order.payment_method == 'cod' and order_status != 'canceled':
        order.payment_status = payment_status

    order.save()

    return JsonResponse({
        'message': 'Order updated successfully',
        'order_id': str(order.id),
        'order_status': order.order_status,
        'payment_status': order.payment_status,
    }, status=200)
    
@login_required(login_url="users:login")
def retrieve_order(request):
    if request.method != "GET":
        return JsonResponse({'error':'Invalid method'},status = 405)
    
    user_id = request.user.id
    user = async_to_sync(verify_user)(user_id=user_id)
    try:
        orders = Orders.objects.filter(user=user).prefetch_related('order_items__product')
    except Orders.DoesNotExist:
        return JsonResponse({'error':'Order doesnot exist'}, status = 404)
    

    data = []
    for order in orders:
        items_data = []
        for item in order.order_items.all():
            items_data.append({
                "id":item.id,
                "product_id": item.product.id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": str(item.price),
                "subtotal": str(item.subtotal),
            })

        data.append({
            "id": order.id,
            "total_amount": str(order.total_amount),
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "delivery_charge": str(order.delivery_charge),
            "order_status": order.order_status,
            "items": items_data,
        })
    context = {
        "order" : data
    }
    return render(request,"ecommerce/order_page.html",context=context)
    # return JsonResponse({'Order':data})

@csrf_exempt
@verify_token
@role_required('customer') 
def delete_order(request,order_id):
    if request.method != "DELETE":
        return JsonResponse({'error':'Invalid method'},status = 405)
    
    user_id = request.user_id
    role = request.role
    order = verify_order(order_id=order_id)
    if isinstance(order, JsonResponse):
        return order
    
    if order.user.id != uuid.UUID(user_id) and role != 'admin':
        return JsonResponse({'error': 'You are not allowed to edit this review'}, status=403)
    
    order.delete()
    return JsonResponse({'message':'Order deleted successfully'})


@login_required
# @role_required('customer') 
def insert_order_item(request):
    if request.method != "POST":
        return JsonResponse({'error':'Invalid method'},status = 405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error':'Failed to decode JSON'},status = 400)
    
    order_id = data.get('order')
    product_id = data.get('product')
    quantity = int(data.get('quantity', 1))
    price = Decimal(str(data.get('price', '0')))
    subtotal = quantity * price

    order = verify_order(order_id=order_id)
    if isinstance(order, JsonResponse):
        return order
    product = verify_product(product_id=product_id)
    if isinstance(product, JsonResponse):
        return product
    if product.stock < quantity:
        return JsonResponse({'message': f'Only {product.stock} items left for {product.name}'}, status=400)

    product.stock -= quantity
    product.save()

    order_item = OrderItem.objects.create(
        order = order,
        product = product,
        quantity = quantity,
        price = price,
        subtotal = subtotal
    )

    return JsonResponse({
        'message': 'Order item created successfully',
        'order_item': {
            'id': order_item.id,
            'order_id': order.id,
            'product': product.name,
            'quantity': quantity,
            'price': str(price),
            'subtotal': str(subtotal),
        }
    }, status=201)


def store_checkout(request):
    if request.method != "POST":
        return JsonResponse({"error":"Invalid Method"},status = 405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error':'Failed to decode JSON'},status = 400)
    
    user_id = request.user.id
    checkout_items = data.get('checkout_items', [])
    
    # Serialize checkout_item as redis hashes only store strings
    checkout_items_serialized = json.dumps(checkout_items)

    # 3. Store in Redis hash
    redis_key = f"user_checkout:{user_id}"
    r.hset(redis_key, mapping={
        "user_id": str(user_id),
        "checkout_items": checkout_items_serialized
    })

    # Set TTL (expire in 15 minute)
    r.expire(redis_key, 900)

    return JsonResponse({"redirect": "/order/checkout"})

def checkout_view(request):
    user_id = request.user.id
    redis_key = f"user_checkout:{user_id}"

    # Get the checkout_items from Redis
    checkout_items_serialized = r.hget(redis_key, "checkout_items")
    if checkout_items_serialized:
        checkout_items = json.loads(checkout_items_serialized)
    else:
        checkout_items = []

    # Calculate total: sum of price * quantity for each item
    total_amount = sum(item['price'] * item['quantity'] for item in checkout_items)
    delivery_charge = 150

    context = {
        "checkout_items": checkout_items,
        "total_product_amount": total_amount,
        "delivery_charge": delivery_charge,
        "total_amount": total_amount + delivery_charge
    }

    return render(request, "ecommerce/checkout_page.html", context)
# def store_checkout(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid Method"}, status=405)

#     user_id = request.user.id
    
#     data = json.loads(request.body)
#     checkout_items = data.get("checkout_items", [])

#     request.session["checkout_items"] = checkout_items  # <-- store in session

#     return JsonResponse({"redirect": "/order/checkout"})
