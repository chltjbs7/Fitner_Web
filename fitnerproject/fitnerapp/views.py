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

def detail(request):
    return render(request, 'detail.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def mypage(request):
    return render(request, 'mypage.html')

def search(request):
    return render(request, 'search.html')