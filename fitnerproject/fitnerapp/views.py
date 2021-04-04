from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home.html')

def day(request):
    return render(request, 'day.html')