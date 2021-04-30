import requests

from isodate import parse_duration

from django.conf import settings
from django.shortcuts import render, redirect

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
    videos = []

    if request.method == 'POST':
        search_url = 'https://youtube.googleapis.com/youtube/v3/search'
        video_url = 'https://youtube.googleapis.com/youtube/v3/videos'
        channel_url = 'https://youtube.googleapis.com/youtube/v3/channels'

        search_params = {
            'part' : 'snippet',
            'q' : request.POST['search'],
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'maxResults' : 1,
            'type' : 'video',
            'videoLicense' : 'creativeCommon'
        }

        r = requests.get(search_url, params=search_params)

        results = r.json()['items']

        video_ids = []
        for result in results:
            video_ids.append(result['id']['videoId'])

        video_params = {
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part' : 'snippet,contentDetails,statistics',
            'id' : ','.join(video_ids),
            'maxResults' : 1
        }

        r = requests.get(video_url, params=video_params)

        results = r.json()['items']

        
        for result in results:
            video_data = {
                'title' : result['snippet']['title'],
                'id' : result['id'],
                'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
                #'duration' : int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                'thumbnail' : result['snippet']['thumbnails']['high']['url'],
                'channelTitle' : result['snippet']['channelTitle'],
                'publishedAt' : result['snippet']['publishedAt'],
                'viewCount' : result['statistics']['viewCount'],
            }

            videos.append(video_data)

    context = {
        'videos' : videos
    }
    return render(request, 'search.html', context)