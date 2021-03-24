from django.urls import path, include
from similarity import views


urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed', views.youtube_feed, name='youtube_feed'),
    path('webcam_feed', views.webcam_feed, name='webcam_feed'),
    ]