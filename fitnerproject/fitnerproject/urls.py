from django.contrib import admin
from django.urls import path
import fitnerapp.views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Page
    path('', fitnerapp.views.home, name='home'),
    path('day/', fitnerapp.views.day, name='day'),
    path('wholebody/', fitnerapp.views.wholebody, name='wholebody'),
    path('videoplayer/', fitnerapp.views.videoplayer, name='videoplayer'),
    path('ytbchannel/', fitnerapp.views.ytbChannel, name='ytbchannel'),
    path('detail/', fitnerapp.views.detail, name='detail'),
    path('login/', fitnerapp.views.login, name='login'),
    path('signup/', fitnerapp.views.signup, name='signup'),
    path('mypage/', fitnerapp.views.mypage, name='mypage'),
]