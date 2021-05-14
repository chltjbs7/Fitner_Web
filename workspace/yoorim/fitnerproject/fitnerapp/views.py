import requests
import pafy
import re
import random

from isodate import parse_duration
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password #비밀번호 암호화 / 패스워드 체크(db에있는거와 일치성확인)
from .models import User
from django.contrib.auth.models import User
from django.contrib import auth
from .models import Ranking
from django.views.decorators.http import condition

# Create your views here.

def home(request):
    return render(request, 'home.html')

def day(request):
    return render(request, 'day.html')

def week(request):
    return render(request, 'week.html')

def month(request):
    return render(request, 'month.html')

def wholebody(request):
    return render(request, 'wholebody.html')

def smartmode(request):
    if request.method=='GET':
        url=request.GET
        video = pafy.new(url['cmd'])
        channel_id=url['channel']
        best = video.getbest(preftype="mp4")

        re_result = re.search('https\:\/\/www\.youtube\.com\/watch\?v\=(\S+)',url['cmd'])
        video_id=re_result.group(1)
        video_url = 'https://youtube.googleapis.com/youtube/v3/videos'

        video_params = {
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part' : 'snippet, statistics',
            'id' : video_id,
        }

        r = requests.get(video_url, params=video_params)
        result = r.json()['items'][0]
        snippet=result['snippet']
        statistics=result['statistics']
        pre_publishedAt=snippet['publishedAt']
        publishedAt_result = re.search('(\d+)\-(\d+)\-(\d+)',pre_publishedAt)
        try:
            tags=snippet["tags"]
            tags_rand=['#'+tags[round(random.randrange(0,len(tags)/4))]+' '+\
            '#'+tags[round(random.randrange(len(tags)/4,len(tags)/4*2))]+' '+\
            '#'+tags[round(random.randrange(len(tags)/4*2,len(tags)/4*3))]+' '+\
            '#'+tags[round(random.randrange(len(tags)/4*3,len(tags)))]]
        except:
            tags_rand=['']
        global data
        data={ 'video_address': best.url,
                'url':url['cmd'],
                'title':snippet['title'],
                'publishedAt':publishedAt_result.group(0),
                'viewCount':statistics['viewCount'],
                'tags':tags_rand[0],
                'channelId':channel_id,
             }
             
    if request.method == "POST":
        username = request.POST.get('username',None)   #딕셔너리형태
        userphone = request.POST.get('userphone',None)
        similarity = request.POST.get('similarity',None)
        if username and userphone :
            ranking = Ranking(username=username, userphone=userphone, similarity=similarity)
            ranking.save()
            #return redirect('smartmode')
    
    return render(request, 'smartmode.html', data)

@csrf_exempt
def videoplayer(request):
    if request.method=='GET':
        url=request.GET
        video = pafy.new(url['cmd'])
        channel_id=url['channel']

        rankings = Ranking.objects.all().order_by('-similarity')[:5]

        best = video.getbest(preftype="mp4")
        re_result = re.search('https\:\/\/www\.youtube\.com\/watch\?v\=(\S+)',url['cmd'])
        video_id=re_result.group(1)
        video_url = 'https://youtube.googleapis.com/youtube/v3/videos'
        channel_url='https://youtube.googleapis.com/youtube/v3/channels'

        video_params = {
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part' : 'snippet, statistics',
            'id' : video_id,
        }

        r = requests.get(video_url, params=video_params)
        result = r.json()['items'][0]
        snippet=result['snippet']
        statistics=result['statistics']
        pre_publishedAt=snippet['publishedAt']
        publishedAt_result = re.search('(\d+)\-(\d+)\-(\d+)',pre_publishedAt)

        try:
            tags=snippet["tags"]
            tags_rand=['#'+tags[round(random.randrange(0,len(tags)/4))]+' '+\
            '#'+tags[round(random.randrange(len(tags)/4,len(tags)/4*2))]+' '+\
            '#'+tags[round(random.randrange(len(tags)/4*2,len(tags)/4*3))]+' '+\
            '#'+tags[round(random.randrange(len(tags)/4*3,len(tags)))]]
        except:
            tags_rand=['']


        channelTitle=snippet["channelTitle"]

        channel_params={
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part':"statistics,snippet",
            'id':channel_id
        }

        channel_r=requests.get(channel_url, params=channel_params)
        channel_result=channel_r.json()['items'][0]
        #print(channel_result['snippet']['thumbnails']['default']['url'])
        data={ 'video_address': best.url,
                'url':url['cmd'],
                'rankings':rankings,
                'title':snippet['title'],
                'publishedAt':publishedAt_result.group(0),
                'viewCount':statistics['viewCount'],
                'tags':tags_rand[0],
                'channelTitle':channelTitle,
                'channelImage':channel_result['snippet']['thumbnails']['default']['url'],
                'channelSubscriber':channel_result['statistics']['subscriberCount'],
                'channelId':channel_id,
             }

    return render(request, 'videoplayer.html', data)

def ytbchannel(request):
    return render(request, 'ytbchannel.html')

def mypage(request):
    return render(request, 'mypage.html')

def user_home(request):
    return render(request, 'user_home.html')

def search(request):
    videos = []
    if request.method == 'POST':
        search_url = 'https://youtube.googleapis.com/youtube/v3/search'
        video_url = 'https://youtube.googleapis.com/youtube/v3/videos'

        search_params = {
            'part' : 'snippet',
            'q' : request.POST['search'],
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'maxResults' : 1,
            'type' : 'video',
            'videoLicense' : 'creativeCommon'
        }

        r = requests.get(search_url, params=search_params)
        result = r.json()['items'][0]
        snippet=result['snippet']
        pre_publishedAt=snippet['publishedAt']
        publishedAt_result = re.search('(\d+)\-(\d+)\-(\d+)',pre_publishedAt)
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
                # 'publishedAt' : result['snippet']['publishedAt'],
                'publishedAt':publishedAt_result.group(0),
                'viewCount' : result['statistics']['viewCount'],
                'channel_id':result['snippet']['channelId']
            }

            videos.append(video_data)
    context = {
        'videos' : videos,
    }
    return render(request, 'search.html', context)

def signup(request):   #회원가입 페이지를 보여주기 위한 함수
    if request.method == "GET":
        return render(request, 'signup.html')

    elif request.method == "POST":
        username = request.POST.get('username',None)   #딕셔너리형태
        password = request.POST.get('password',None)
        re_password = request.POST.get('re_password',None)
        res_data = {} 
        if not (username and password and re_password) :
            res_data['error'] = "모든 값을 입력해야 합니다."
        if password != re_password :
            # return HttpResponse('비밀번호가 다릅니다.')
            res_data['error'] = '비밀번호가 다릅니다.'
        else :
            user = User(username=username, password=make_password(password))
            user.save()
            return redirect('login')
        return render(request, 'signup.html', res_data) #signup 요청받으면 signup.html 로 응답.

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(
            request, username=username, password=password
        )

        if user is not None:
            auth.login(request, user)
            return redirect('user_home')
        else:
            return render(request, "login.html", {
                'error': '비밀번호가 틀렸습니다.',
            })
    else:
        return render(request, "login.html")