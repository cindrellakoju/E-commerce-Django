from django.shortcuts import render

def view_chat(request):
    return render(request, 'ecommerce/chat_app.html')