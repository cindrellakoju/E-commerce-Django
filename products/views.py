from products.models import ProductCategory
import json
from django.http import JsonResponse
from users.services import verify_token,role_required
from django.views.decorators.csrf  import csrf_exempt
from django.utils.text import slugify
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