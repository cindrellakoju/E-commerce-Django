# # from django.shortcuts import render
# import json
# from django.http import JsonResponse
# import uuid
# # Create your views here.
# def generate_presigned_url(request):
#     if request.method != "POST":
#         return JsonResponse({'error':'Invalid method'},status = 405)
    
#     try:
#         data = json.loads(request.body)
#     except json.JSONDecodeError:
#         return JsonResponse({'error':'Failed to decode JSON'},status = 400)
    
#     filename = data.get('filename')
#     content_type = data.get('content_type')
#     user_id = request.user_id
#     document_type = regenerquest.get('document_type')
#     doc_id = str(uuid.uuid4())

#     s3_key = (
#         f"employees/{data.employee_id}/{data.document_type}/{doc_id}_{data.filename}"
#     )



    