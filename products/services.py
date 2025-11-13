from django.core.paginator import Paginator,EmptyPage
from django.http import JsonResponse
from products.models import Products

def pagination(page_number,page_size,products):
    paginator=Paginator(products,page_size)

    try:
        paginate_product = paginator.get_page(page_number)
    except EmptyPage:
        # return JsonResponse({'message':'No product remaining'},status = 200)
        return {
            'page': page_number,
            'total_pages': 0,
            'total_products': 0,
            'products': []
        }

    
    data = []
    for product in paginate_product:
        data.append({
            'id':str(product.id),
            'seller' : str(product.seller),
            'category' : str(product.category),
            'name':product.name,
            'slug':product.slug,
            'description':product.description,
            'price':product.price,
            'stock':product.stock
        })
    # return JsonResponse({
    #     'page': paginate_product.number,
    #     'total_pages': paginator.num_pages,
    #     'total_products': paginator.count,
    #     'products': data
    # }, status=200)
    return {
        'page': paginate_product.number,
        'total_pages': paginator.num_pages,
        'total_products': paginator.count,
        'products': data
    }

def verify_product(product_id):
    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        return JsonResponse({'error':'Product not found'},status = 404)
    return product