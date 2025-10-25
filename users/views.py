from django.http import HttpResponse

async def index(request):
    return HttpResponse("Hello from user")
# Create your views here.
