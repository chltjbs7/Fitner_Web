from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home.html')

def day(request):
    return render(request, 'day.html')

def wholebody(request):
    return render(request, 'wholebody.html')

def videoplayer(request):
    return render(request, 'videoplayer.html')

def ytbChannel(request):
    return render(request, 'ytbchannel.html')