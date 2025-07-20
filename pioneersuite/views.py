from django.shortcuts import render

def custom_403_view(request, exception=None):
    return render(request, "unauthorized.html", {
        "message": "Sorry, you don’t have permission to view this page."
    }, status=403)
