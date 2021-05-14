from django.contrib import admin
from .models import User   #같은 경로의 models.py에서 User라는 클래스를 임포트한다.
from .models import Ranking
from .models import Data


# Register your models here.

class UserAdmin(admin.ModelAdmin) :
    list_display = ('username', 'password')

admin.site.register(User, UserAdmin) #site에 등록

class RankingAdmin(admin.ModelAdmin):
    list_display = ('username', 'userphone', 'similarity', 'registered_dttm')
 
admin.site.register(Ranking, RankingAdmin)

class DataAdmin(admin.ModelAdmin):
    list_display = ('videoId', 'high', 'low', 'average', 'high_img_route', 'low_img_route', 
    'high_start_section', 'high_end_section', 'low_start_section', 'low_end_section', 'total_time', 'registered_dttm')
 
admin.site.register(Data, DataAdmin)