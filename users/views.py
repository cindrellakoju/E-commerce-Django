from django.http import HttpResponse,JsonResponse
from users.models import Users
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
import json
from users.services import generate_jwt, verify_token
from django.contrib.auth.hashers import check_password
import datetime

@verify_token
def index(request):
    user_id = request.user_id
    # user = Users(username="cindrella",email="cindrellakoju@gmail.com",password="1234",phone="9840347840",roles="admin")
    # user = Users.objects.get(username="cindrella")
    # user.phone="9864163280"
    # user.save()
    return JsonResponse({
        "message": "This is a protected view",
        "user_id": user_id
    })
# Create your views here.

def results(request, question_id):
    print(request.method)
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

@csrf_exempt
def signup(request):
    if request.method == "POST":
        try:
            data= json.loads(request.body)
            username = data.get("username")
            email = data.get("email")
            password = data.get('password')
            phone = data.get('phone')
            roles = data.get('roles')
        except ValueError:
            return JsonResponse({"error":"Invalid JSON"},status=400)
        
        if not username or not email or not password or not phone or not roles:
            return JsonResponse({"error" : "All fields are required"},status = 400)
        
        if Users.objects.filter(username=username).exists():
            return JsonResponse({"error":"Username already exist"},status = 400)
        
        if Users.objects.filter(email=email).exists():
            return JsonResponse({"error":"Email already exist"},status = 400)
        
        user = Users.objects.create(
            username = username,
            email = email,
            password = make_password(password),
            phone = phone,
            roles = roles
        )

        return JsonResponse({"message":"User created successfully","username" : user.username})
    return JsonResponse({"error":"Failed to create user"},status = 400)

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
        except ValueError:
            return JsonResponse({"error":"Invalid JSON"},status = 400)
        
        if not email or not password:
            return JsonResponse({"error":"Email or password required"},status = 400)
        
        user = Users.objects.filter(email=email).first()
        if user and check_password(password,user.password):
            user.last_login = datetime.datetime.utcnow()
            user.save()
            # token = 'rerer'
            token = generate_jwt(user.id,email)
            return JsonResponse({"message":"Login successful","token_type" : "Bearer","token" : token})
        else:
            return JsonResponse({"error":"Invalid email or password"},status = 401)
    else:
        return JsonResponse({'error': 'POST request required'}, status=400)