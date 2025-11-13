from products.models import ProductCategory, Products, ProductImage, ProductReview
import json
from django.http import JsonResponse
from users.services import verify_token,role_required,verify_user
from django.views.decorators.csrf  import csrf_exempt
from django.utils.text import slugify
from products.services import pagination
from django.db.models import Q
import uuid
from products.services import verify_product
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseNotAllowed
# Create your views here.
@csrf_exempt
@verify_token
@role_required('admin')
def create_category(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            parent_id = data.get("parent_id")
            
            if not name:
                return JsonResponse({"error": "Category name is required"}, status=400)

            parent_category = None
            if parent_id:
                try:
                    parent_category = ProductCategory.objects.get(id=parent_id)
                except ProductCategory.DoesNotExist:
                    return JsonResponse({"error": "Parent category not found"}, status=404)

            category = ProductCategory.objects.create(
                name=name,
                parent_id=parent_category
            )

            return JsonResponse({
                "message": "New category added successfully",
                "category_name": category.name,
                "slug_name":category.slug,
                "category_id": str(category.id)
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Failed to create new category"}, status=400)

@csrf_exempt
@verify_token
@role_required('admin')
def edit_category(request, slug):
    if request.method in ['PUT','PATCH']:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error":"Invalid JSON"},status = 400)
        
        try:
            category = ProductCategory.objects.get(slug=slug)
        except ProductCategory.DoesNotExist:
            return JsonResponse({"error":"Product Category does not exist"},status = 404)
        
        name = data.get("name")
        if name:
            category.name = name
            category.slug = slugify(name)

        parent_id = data.get("parent_id")
        if parent_id:
            if category.id ==  parent_id:
                return JsonResponse({"error":"Categoty and parents cannot be same"},status=400)
            try:
                parent_category = ProductCategory.objects.get(id=parent_id)
                category.parent_id = parent_category
            except ProductCategory.DoesNotExist:
                return JsonResponse({"error":"Product Category does not exist"},status = 404)
        category.save()

        return JsonResponse({
            "message" : "Product category updated successfully"
        })
    return JsonResponse({'error':"Invalid request method"},status = 405)

@csrf_exempt
@verify_token
@login_required(login_url="users:login")
def retrieve_category(request):
    categories = ProductCategory.objects.all()
    
    if not categories.exists():
        return JsonResponse({'error': "No categories found"}, status=404)
    
    # Serialize categories into a list of dicts
    data = []
    for category in categories:
        data.append({
            "id": str(category.id),  # UUID needs to be converted to string
            "name": category.name,
            "slug": category.slug,
            "parent_id": str(category.parent_id.id) if category.parent_id else None
        })
    
    return JsonResponse({"categories": data}, status=200)

@csrf_exempt
@verify_token
@role_required('admin')
def delete_category(request,slug):
    if request.method == "DELETE":
        try:
            category = ProductCategory.objects.get(slug=slug)
        except ProductCategory.DoesNotExist:
            return JsonResponse({'error':"Category doesnot exist"},status = 404)

        category.delete()
        return JsonResponse({"message":f"Category of slog {slug} deleted successfully"})
    
@csrf_exempt
@verify_token
@role_required('admin','seller')   
def create_product(request):
    pass
    if request.method == "POST":
        try:
            user_id = request.user_id
            data = json.loads(request.body)
            category_id = data.get('category')
            name = data.get('name')
            description = data.get('description')
            price = data.get('price')
            stock = data.get('stock')

            seller = verify_user(user_id=user_id)
            if isinstance(seller, JsonResponse):
                return seller
            try:
                category = ProductCategory.objects.get(id=category_id)
            except ProductCategory.DoesNotExist:
                return JsonResponse({'error':'Category doesnot exist'},status=404)
            
        except json.JSONDecodeError:
            return JsonResponse({'error':'Invalid json format'},status = 400)
        
        product = Products.objects.create(
            seller = seller,
            category = category,
            name = name,
            description = description,
            price = price,
            stock = stock
        )

        return JsonResponse({'message':'New Product added successfully','product_id': str(product.id)})
    return JsonResponse({'error':"Invalid request method"},status = 405)

@csrf_exempt
@verify_token
@role_required('admin','seller')  
def edit_product(request,slug):
    if request.method in ["PUT","PATCH"]:
        try:
            data = json.loads(request.body)
            category = data.get('category')
            name = data.get('name')
            description = data.get('description')
            price = data.get('price')
            stock = data.get('stock')
            try:
                product = Products.objects.get(slug=slug)
            except Products.DoesNotExist:
                return JsonResponse({'error':"product Does not exist"},status = 404)
        except ValueError:
            return JsonResponse({'error':'Invalid json format'},status = 400)
        
        if category:
            product.category = category

        if name:
            product.name = name
            product.slug = slugify(name)

        if description:
            product.description = description

        if price:
            product.price = price

        if stock:
            product.stock = stock

        product.save()
        return JsonResponse({'message':"Product updated sucessfully"})
    return JsonResponse({'error':"Invalid method"},status = 405)

@csrf_exempt
@login_required(login_url="users:login")
def retrieve_product(request):
    if request.method == "GET":
        try:
            products = Products.objects.all()   
        except Products.DoesNotExist:
            return JsonResponse({"error":"Product does not exist"},status = 404)
        
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('size', 5))

        
        pagination_data = pagination(page_number=page_number, page_size=page_size, products=products)
        page_number = pagination_data['page']
        total_pages = pagination_data['total_pages']
        total_product = pagination_data['total_products']
        products = pagination_data['products']
        context = {
            'page_number': page_number,
            'total_pages': total_pages,
            'total_products': total_product,
            'products': products
        }

        return render(request,"ecommerce/home_page.html",context=context)
    # Handle non-GET requests
    return HttpResponseNotAllowed(['GET'])

@csrf_exempt
@verify_token
@role_required('admin','seller')   
def delete_product(request,slug):
    if request.method == "DELETE":
        try:
            product = Products.objects.get(slug=slug)
        except Products.DoesNotExist:
            return JsonResponse({'error':"product Does not exist"},status = 404)
        
        product.delete()
        return JsonResponse({"error":"Product deleted successfully"})
    return JsonResponse({'error':"Invalid method"},status = 405)

@csrf_exempt
@verify_token
@role_required('admin','seller')  
def add_image(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product = data.get('product')
            image_url = data.get('image_url')
            is_main = data.get('is_main')
        except json.JSONDecodeError:
            return JsonResponse({'error':'Invalid json format'},status = 400)
        try:
            products = Products.objects.get(id=product)
        except Products.DoesNotExist:
            return JsonResponse({'error':"product Does not exist"},status = 404)
        
        image = ProductImage.objects.create(
            product = products,
            image_url = image_url,
            is_main = is_main
        )
        return JsonResponse({'message':'Image added successfully','image_id': str(image.id)})
    return JsonResponse({'error':"Invalid request method"},status = 405)

@csrf_exempt
@verify_token
@role_required('admin','seller') 
def delete_image(request,image_id):
    if request.method == "DELETE":
        try:
            image = ProductImage.objects.get(id=image_id)
        except ProductImage.DoesNotExist:
            return JsonResponse({'error':"Image Does not exist"},status = 404)
        
        image.delete()
        return JsonResponse({"error":"Image deleted successfully"})
    return JsonResponse({'error':"Invalid method"},status = 405)

@csrf_exempt
@verify_token
def search_engine(request):
    if request.method == "GET":
        search_contain = request.GET.get("search","")
        sort_option = request.GET.get("sort","recently_added")
        category_name = request.GET.get("category", "").strip()
        
        results = Products.objects.all()
    
        if not results.exists():
            return JsonResponse({'error': "No product found"}, status=404)

        if search_contain:
            results = Products.objects.filter(
                Q(name__icontains=search_contain) |
                Q(description__icontains=search_contain) |
                Q(category__name__icontains=search_contain)
            )
        
        if category_name:
            results = results.filter(category__name__iexact=category_name)

        if sort_option == "highest_price":
            results = results.order_by("-price")
        elif sort_option == "lowest_price":
            results = results.order_by("price")
        elif sort_option == "recently_added":
            results = results.order_by("-created_at")
        else:
            results = results.order_by("-created_at")
        
        page_number = request.GET.get('page',1)
        page_size = request.GET.get('size',5)
        return pagination(page_number=page_number,page_size=page_size,products=results)
    return JsonResponse({'error':"Invalid method"},status = 405)

@csrf_exempt
@verify_token
@role_required('customer') 
def create_product_review(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = request.user_id
            product_id= data.get("product")
            review_msg = data.get("review_msg")
            review_star = data.get("review_star")
        except json.JSONDecodeError:
            return JsonResponse({'error':'Failed to decode JSON'},status = 400)
        
        user = verify_user(user_id)
        if isinstance(user, JsonResponse):
            return user
        product = verify_product(product_id=product_id)
        if isinstance(product, JsonResponse):
            return product
        review = ProductReview.objects.create(
            reviewer = user,
            product = product,
            review_msg = review_msg,
            review_star = review_star
        )

        return JsonResponse({'message':'Review Added successfully','review_id':review.id})
    return JsonResponse({'error':"Invalid method"},status = 405)

@csrf_exempt
@verify_token
@role_required('customer') 
def edit_product_review(request,review_id):
    if request.method in ["PUT","PATCH"]:
        try:
            data = json.loads(request.body)
            user_id = request.user_id
            review_msg = data.get("review_msg")
            review_star = data.get("review_star")
            review = ProductReview.objects.get(id=review_id)
        except ProductReview.DoesNotExist:
            return JsonResponse({'error':'Product Review doesnot exist'},status = 404)

        if review.reviewer.id != uuid.UUID(user_id):
            return JsonResponse({'error': 'You are not allowed to edit this review'}, status=403)
        
        if review_msg:
            review.review_msg = review_msg

        if review_star:
            review.review_star = review_star

        review.save()
        return JsonResponse({'message':'Review Updated successfully'})
    return JsonResponse({'error':"Invalid method"},status = 405)

@csrf_exempt
@verify_token
def retrieve_product_review(request,product_id):
    if request.method == "GET":
        try:
            review = ProductReview.objects.filter(product = product_id).order_by('review_star')
        except ProductReview.DoesNotExist:
            return JsonResponse({'error':'Product Review doesnot exist'},status = 404)
        
        data = []
        for product_review in review:
            data.append({
                "id" : str(product_review.id),
                "reviewer" : product_review.reviewer.username,
                "review_msg":product_review.review_msg,
                "review_star":product_review.review_star
            })
        return JsonResponse({"Product Review":data})
    return JsonResponse({'error':"Invalid method"},status = 405)

@csrf_exempt
@verify_token
@role_required('customer','admin') 
def delete_product_review(request,review_id):
    if request.method == "DELETE":
        try:
            user_id = request.user_id
            role = request.role
            review = ProductReview.objects.get(id=review_id)
        except ProductReview.DoesNotExist:
            return JsonResponse({'error':'Product Review doesnot exist'},status = 404)

        if review.reviewer.id != uuid.UUID(user_id) and role != 'admin':
            return JsonResponse({'error': 'You are not allowed to edit this review'}, status=403)
        
        review.delete()
        return JsonResponse({"message":"Review deleted successfully"})
    return JsonResponse({'error':"Invalid method"},status = 405)
