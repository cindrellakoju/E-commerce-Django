
# from django.shortcuts import render
from pathlib import Path
from dotenv import load_dotenv
from users.services import verify_user
from orders.services import verify_order
from orders.models import OrderItem,Orders
from django.http import JsonResponse
import os
import requests
from django.views.decorators.csrf import csrf_exempt
from payments.models import Payment
import json
from django.contrib.auth.decorators import login_required
from asgiref.sync import async_to_sync
# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

url = "https://dev.khalti.com/api/v2/epayment/initiate/"
KHALTI_REFUND_URL = "https://dev.khalti.com/api/merchant-transaction/{transaction_id}/refund/"
secret_key = os.getenv('KHALTI_LIVE_SECRET_KEY')
headers = {
    'Authorization': f'Key {secret_key}',
    'Content-Type': 'application/json',
}

def map_khalti_status(khalti_status):
    if khalti_status not in ["Completed", "Failed", "Pending"]:
        print(f"Warning: Unknown Khalti status: {khalti_status}")
    if khalti_status == "Completed":
        return "success"
    elif khalti_status == "Failed":
        return "failed"
    else:
        return "pending"


@login_required(login_url="users:login")
def khalti_payment(request, order_id):
    if request.method != "POST":
        return JsonResponse({'error': "Invalid Method"}, status=405)

    user_id = request.user.id


    user = async_to_sync(verify_user)(user_id=user_id)
    if isinstance(user, JsonResponse):
        return user
    order = verify_order(order_id=order_id)
    if isinstance(order, JsonResponse):
        return order


    if order.total_amount is None:
        return JsonResponse({'error': "total_amount is required"}, status=400)
    total_amount = int(float(order.total_amount) * 100) 

    order_items = OrderItem.objects.filter(order=order)
    if not order_items.exists():
        return JsonResponse({'error': 'Order items not found'}, status=404)

    item_details = []
    item_names = []

    for item in order_items:
        item_details.append({
            "id": str(item.id),
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": float(item.price),  # Decimal -> float
            "subtotal": float(item.subtotal)
        })
        item_names.append(item.product.name)

    purchase_order_name = ", ".join(item_names)

    khalti_payload = {
        "return_url": f"http://localhost:8000/payments/khalti/verify/{order_id}",   # your return URL
        "website_url" : "http://localhost:8000",
        "amount": total_amount,
        "purchase_order_id": str(order.id),
        "purchase_order_name": purchase_order_name,
        "customer_info": {
            "name": user.fullname,
            "email": user.email,
            "phone": user.phone
        },
        "order_item_details": item_details
    }

    response = requests.post(
        url,
        headers=headers,
        json=khalti_payload
    )
    try:
        response_data = response.json()
    except ValueError:
        return JsonResponse({'error': 'Invalid response from Khalti'}, status=500)
    

    return JsonResponse(response_data, status=response.status_code)


@csrf_exempt
@login_required(login_url="users:login")
def verify_khalti_payment(request, order_id):
    if request.method != "GET":
        return JsonResponse({'error': "Invalid Method"}, status=405)

    lookup_url = "https://dev.khalti.com/api/v2/epayment/lookup/"
    pidx = request.GET.get("pidx")

    if not pidx or not order_id:
        return JsonResponse({'error': 'pidx and order_id are required'}, status=400)

    try:
        order = verify_order(order_id=order_id)
        if isinstance(order, JsonResponse):
            return order
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

    payload = {'pidx': pidx}  # dict, not json.dumps

    

    try:
        response = requests.post(lookup_url, headers=headers, json=payload)
        response_data = response.json()
    except Exception as e:
        return JsonResponse({'error': 'Failed to verify with Khalti', 'details': str(e)}, status=500)

    khalti_status = response_data.get("status")
    payment_status = map_khalti_status(khalti_status)

    # ⚠️ Check for duplicate pidx BEFORE creating
    if Payment.objects.filter(pidx=response_data.get("pidx")).exists():
        return JsonResponse({
            "error": "Payment with this pidx already exists",
        }, status=400)

    payment_info = Payment.objects.create(
        order=order,
        transaction_id=response_data.get("transaction_id"),
        pidx=response_data.get("pidx"),
        payment_status=payment_status,
        refunded=response_data.get("refunded", False),
        refund_status="not_requested"
    )

    order = Orders.objects.get(id=order_id)
    order.payment_status = 'paid'
    order.save()

    return JsonResponse({
        "message": "Payment verified successfully",
        "payment": {
            "transaction_id": payment_info.transaction_id,
            "pidx": payment_info.pidx,
            "payment_status": payment_info.payment_status,
            "refunded": payment_info.refunded,
            "refund_status": payment_info.refund_status
        }
    })

@csrf_exempt
@login_required(login_url="users:login")
def refund_khalti_payment(request,order_id):
    if request.method != "POST":
        return JsonResponse({'error': "Invalid Method"}, status=405)
    
    order = verify_order(order_id=order_id)
    if isinstance(order, JsonResponse):
        return order
    
    try:
        body = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        body = {}

    amount = body.get('amount')
    mobile = body.get('mobile')

    payload = {}
    if amount is not None:
        payload['amount'] = amount
    if mobile is not None:
        payload['mobile'] = mobile
    try:
        payment_info = Payment.objects.get(order=order)
    except Payment.DoesNotExist:
        return JsonResponse({"error":"Payment doesnot exist"},status = 400)
    
    # ⚠️ Prevent double refunds
    if payment_info.refunded and payment_info.refund_status in ['processed', 'rejected']:
        return JsonResponse({
            "error": "Refund already processed or rejected for this payment",
            "refund_status": payment_info.refund_status
        }, status=400)
    
    url = KHALTI_REFUND_URL.format(transaction_id=payment_info.transaction_id)

    response = requests.post(url,headers=headers,json=payload)

    try:
        resp_json = response.json()
    except ValueError:
        return JsonResponse({'error': 'Invalid response from Khalti'}, status=500)

    if response.status_code == 200:
        payment_info.refunded = True
        payment_info.refund_status = 'processed'
        payment_info.save()
        return JsonResponse(resp_json, status=200)
    else:
        payment_info.refund_status = 'failed'
        payment_info.save()
        print(f"Khalti refund failed: {resp_json}")
        return JsonResponse(resp_json, status=response.status_code)