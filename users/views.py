
"""With JWT token"""

# from django.http import HttpResponse,JsonResponse
# from users.models import Users
# from django.contrib.auth.hashers import make_password
# from django.views.decorators.csrf import csrf_exempt
# import json
# from users.services import generate_jwt, verify_token
# from django.contrib.auth.hashers import check_password
# import datetime
# from django.shortcuts import render

# @verify_token
# def index(request):
#     user_id = request.user_id
#     # user = Users(username="cindrella",email="cindrellakoju@gmail.com",password="1234",phone="9840347840",roles="admin")
#     # user = Users.objects.get(username="cindrella")
#     # user.phone="9864163280"
#     # user.save()
#     return JsonResponse({
#         "message": "This is a protected view",
#         "user_id": user_id
#     })
# # Create your views here.

# def results(request, question_id):
#     print(request.method)
#     response = "You're looking at the results of question %s."
#     return HttpResponse(response % question_id)

# @csrf_exempt
# def signup(request):
#     if request.method == "POST":
#         try:
#             data= json.loads(request.body)
#             username = data.get("username")
#             email = data.get("email")
#             password = data.get('password')
#             phone = data.get('phone')
#             roles = data.get('roles')
#         except ValueError:
#             return JsonResponse({"error":"Invalid JSON"},status=400)
        
#         if not username or not email or not password or not phone or not roles:
#             return JsonResponse({"error" : "All fields are required"},status = 400)
        
#         if Users.objects.filter(username=username).exists():
#             return JsonResponse({"error":"Username already exist"},status = 400)
        
#         if Users.objects.filter(email=email).exists():
#             return JsonResponse({"error":"Email already exist"},status = 400)
        
#         user = Users.objects.create(
#             username = username,
#             email = email,
#             password = make_password(password),
#             phone = phone,
#             roles = roles
#         )

#         return JsonResponse({"message":"User created successfully","username" : user.username})
#     return JsonResponse({"error":"Failed to create user"},status = 400)

# @csrf_exempt
# def login_view(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             password = data.get('password')
#         except ValueError:
#             return JsonResponse({"error":"Invalid JSON"},status = 400)
        
#         if not email or not password:
#             return JsonResponse({"error":"Email or password required"},status = 400)
        
#         user = Users.objects.filter(email=email).first()
#         if user and check_password(password,user.password):
#             user.last_login = datetime.datetime.utcnow()
#             user.save()
#             # token = 'rerer'
#             token = generate_jwt(user.id,email,user.roles)
#             return JsonResponse({"message":"Login successful","token_type" : "Bearer","token" : token})
#         else:
#             return JsonResponse({"error":"Invalid email or password"},status = 401)
#     else:
#         return JsonResponse({'error': 'POST request required'}, status=400)
    
# @verify_token
# def login_user(request):
#     if request.method != "GET":
#         return JsonResponse({'error':'Invalid Method'},status = 405)
#     user_id = request.user_id
#     try:
#         user = Users.objects.get(id = user_id)
#     except Users.DoesNotExist:
#         return JsonResponse({'error':'User doesnot exist'},status = 404)
    
#     user_info = {
#         "id" : user_id,
#         "username" : user.username,
#         "email" : user.email,
#         "fullname" : user.fullname,
#         "phone" : user.phone,
#         "secondary_contact_number" : user.secondary_contact_number,
#         "address": user.address,
#         "roles" : user.roles
#     }
#     return render(request,'ecommerce/user_profile.html',user_info)


# With Session
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from users.models import Users
from django.contrib.auth.hashers import make_password
from document.utils import generate_presigned_url

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # authenticate works with custom user model (AUTH_USER_MODEL)
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)  # stores user in session
            return redirect('users:profile')  # use URL name, not relative path
        else:
            messages.error(request, "Invalid email or password")
            return redirect('users:login')

    return render(request, 'ecommerce/login.html')  # render login form


def logout_view(request):
    logout(request)  # clears the session
    return redirect('users/login/')

@login_required(login_url='users:login')
def profile(request):
    user = request.user
    profile_image_url = None

    if user.profile_image:
        # Use exactly the stored name; storage location is already handled
        profile_image_url = generate_presigned_url(user.profile_image.name)
 
    print("Profile Image URL:",profile_image_url)
    return render(request, 'ecommerce/user_profile.html', {
        "fullname": user.fullname,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "address": user.address,
        "roles": user.roles,
        "profile_image": profile_image_url
    })


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        roles = request.POST.get("roles")
        profile_image = request.FILES.get("profile_image")  # file upload

        if not username or not email or not password or not phone or not roles:
            return JsonResponse({"error": "All fields are required"}, status=400)

        if Users.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)
        if Users.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists"}, status=400)

        user = Users.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            phone=phone,
            roles=roles,
            profile_image=profile_image
        )

        return JsonResponse({
            "message": "User created successfully",
            "username": user.username,
        })

    # GET request → render signup page
    return render(request, "ecommerce/signup_page.html")