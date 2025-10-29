import jwt
import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
from functools import wraps
from django.http import JsonResponse
from users.models import Users

BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)
load_dotenv(BASE_DIR/'.env')
secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM", "HS256")  # default to HS256 if not in .env

def generate_jwt(userid,email,role):
    payload = {
        "user_id" : str(userid),
        "email" : email,
        "role" : role,
        "exp" :  datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token

def verify_token(view_func):
    @wraps(view_func)
    def _wrapped_view(request,*args,**kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            JsonResponse({"error" : "Authorization header is missing"},status = 401)
        else:
            try:
                token_type, token = auth_header.split()
                if token_type.lower() != 'bearer':
                    raise ValueError("Invalid token type")
            except ValueError:
                return JsonResponse({"error": "Invalid Authorization header"}, status=401)
                
            try:
                payload = jwt.decode(
                    token,
                    secret_key,
                    algorithm
                )
                request.user_id = payload["user_id"]
                request.role = payload["role"]
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token expired"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "Invalid token"}, status=401)
            
            return view_func(request, *args, **kwargs)
    return _wrapped_view

def role_required(*allowed_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request,*args,**kwargs):
            user_id = getattr(request,"user_id",None)
            if not user_id:
                return JsonResponse({"error":"Unauthorized"},status = 401)
            
            try:
                user = Users.objects.get(id=user_id)
            except Users.DoesNotExist:
                return JsonResponse({"error":"User doesnot exist"},status = 404)
            
            if user.roles not in allowed_role:
                return JsonResponse({"error":"Access denied.No required role "},status = 403)
            return view_func(request,*args,**kwargs)
        return _wrapped_view
    return decorator

def verify_user(user_id):
    try:
        user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return JsonResponse({'error':'User not found'},status = 404)
    return user