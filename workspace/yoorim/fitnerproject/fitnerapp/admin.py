from django.contrib import admin
from .models import User   #같은 경로의 models.py에서 User라는 클래스를 임포트한다.
from .models import Rank
from .models import Data
from .models import Playlist
from .models import Subscribe

# Register your models here.

class UserAdmin(admin.ModelAdmin) :
    list_display = ('username', 'password')

admin.site.register(User, UserAdmin) #site에 등록

class RankAdmin(admin.ModelAdmin):
    list_display = ('videoId', 'username', 'userphone', 'similarity', 'registered_dttm')
 
admin.site.register(Rank, RankAdmin)

class DataAdmin(admin.ModelAdmin):
    list_display = ('videoId', 'high', 'low', 'average', 'high_img_route', 'low_img_route', 
    'high_start_section', 'high_end_section', 'low_start_section', 'low_end_section', 'total_time', 'registered_dttm')
 
admin.site.register(Data, DataAdmin)

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('videoName', 'videoId', 'registered_dttm')
 
admin.site.register(Playlist, PlaylistAdmin)

class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('channelId', 'registered_dttm')
 
admin.site.register(Subscribe, SubscribeAdmin)