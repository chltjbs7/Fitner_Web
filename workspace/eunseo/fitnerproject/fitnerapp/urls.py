from django.contrib import admin
from django.urls import path
import fitnerapp.views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Page
    path('', fitnerapp.views.home, name='home'),

    path('wholebody/', fitnerapp.views.wholebody, name='wholebody'),

    path('day/', fitnerapp.views.day, name='day'),
    path('week/', fitnerapp.views.week, name='week'),
    path('month/', fitnerapp.views.month, name='month'),

    path('videoplayer/', fitnerapp.views.videoplayer, name='videoplayer'),
    path('ytbchannel/', fitnerapp.views.ytbchannel, name='ytbchannel'),

    path('login/', fitnerapp.views.login, name='login'),
    path('signup/', fitnerapp.views.signup, name='signup'),

    path('user_home/', fitnerapp.views.user_home, name='user_home'),
    path('mypage/', fitnerapp.views.mypage, name='mypage'),
    path('playlist/', fitnerapp.views.playlist, name='playlist'),
    path('allViewRecord/', fitnerapp.views.allViewRecord, name='allViewRecord'),

    path('search/', fitnerapp.views.search, name='search'),
    path('smartmode/', fitnerapp.views.smartmode, name='smartmode'),

    path('barChart/', fitnerapp.views.barChart, name='barChart'),
]