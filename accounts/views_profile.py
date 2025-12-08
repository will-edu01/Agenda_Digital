from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


@login_required
def update_profile(request):
    if request.method == "POST":
        user = request.user
        user.name = request.POST.get("name")
        user.phone = request.POST.get("phone")
        user.save()

        return JsonResponse({
            "success": True,
            "name": user.name,
            "phone": user.phone
        })

    return JsonResponse({"success": False})
