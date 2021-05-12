from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from fitnerapp.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('fitnerapp.urls')), #폴더.파일명
    #즉, user/ 이하 url들은 myuser폴더의 urls에서 관리하도록한다.라는 설정
    path('', home),
]