from products.models import ProductCategory
import json
from django.http import JsonResponse
from users.services import verify_token,role_required
from django.views.decorators.csrf  import csrf_exempt
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

