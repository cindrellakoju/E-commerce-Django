from django.shortcuts import render
from django_redis import get_redis_connection
from django.http import JsonResponse

def videocallpage(request,user_id):
    user = request.user
    r = get_redis_connection("default")
    r.sadd("online_users", str(user.id))
    context = {
        "receiver_id": user_id      # Optional: the user being called
    }
    print("Hitt",user_id)
    return render(request, "ecommerce/videocall.html", context)

# New view to remove user
def remove_online_user(request):
    if request.method == "POST":
        user = request.user
        r = get_redis_connection("default")
        r.srem("online_users", str(user.id))
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)
