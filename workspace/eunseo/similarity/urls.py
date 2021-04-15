from django.urls import path, include
from similarity import views


urlpatterns = [
    path('', views.index, name='index'),
    #path('youtube_feed', views.youtube_feed, name='youtube_feed'),
    path('webcam_feed', views.webcam_feed, name='webcam_feed'),
    path('stream_response', views.stream_response, name='stream_response')
    #path('get_stream', views.get_stream, name='get_stream')
    ]