# accesscontrol/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'accesscontrol/home.html')
