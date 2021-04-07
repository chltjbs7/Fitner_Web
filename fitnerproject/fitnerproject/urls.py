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
]