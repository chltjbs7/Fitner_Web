import requests
import pafy
import re
import random
import os
import shutil

from datetime import datetime, timedelta
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
from .models import Data
from django.db.models import Sum
from django.db.models import Count

# Create your views here.

def home(request):
    return render(request, 'home.html')

def allViewRecord(request):
    return render(request, 'allViewRecord.html')

def playlist(request):
    return render(request, 'playlist.html')

def barChart(request):
    labels = []
    data = []

    # 그래프(운동 시간으로 나타냄)
    #t_day = Data.objects.values('total_time')
    today_data=Data.objects.filter(registered_dttm__date=datetime.date(datetime.now()).isoformat()).all()
    today_data_values=today_data.values()
    graph_data={}
    graph_data_list=[]
    index=[0,]
    for i in today_data_values:
        a=datetime.time(i["registered_dttm"]).hour
        start=0
        end=3
        for j in range(8):
            if a>=start and a<end:
                if str(start) not in graph_data:
                    graph_data[str(start)]={"x": str(start)+"시", "y": i["total_time"]}
                else:
                    graph_data[str(start)]["y"]+=i["total_time"]
                start+=3
                end+=3
    for i in graph_data.values():
        graph_data_list.append(i)

    
    return render(request, 'barChart.html', {
        'graph_data':graph_data_list
    })

def day(request):
    if request.method=='GET':
        r=request.GET
        try:
            yesterday = r['yesterday']
            print(yesterday)
        
            now=yesterday
        except:
            now=datetime.now()
    # 총 운동 시간
    #time_sum = Data.objects.aggregate(Sum('total_time'))
    time_filter=Data.objects.filter(registered_dttm__date=datetime.date(now).isoformat()).aggregate(Sum('total_time'))
    print(time_filter)
    #t_values = time_sum.values()
    t_values=time_filter.values()

    for i in t_values:
        t_values = i

    t_value_sec=t_values

    hours = t_values // 3600
    t_values = t_values - hours*3600
    mu = t_values // 60
    ss = t_values - mu*60
    #print(hours, '시간', mu, '분', ss, '초')

    # 운동한 영상
    #video = Data.objects.annotate(Count('videoId'))
    video = Data.objects.filter(registered_dttm__date=datetime.date(now).isoformat()).annotate(Count('videoId'))
    v_values = list(video.values_list('videoId'))
    video_cnt = len(v_values)
    #print(video_cnt)

    # 전날 대비 운동량
    yesterday_filter=Data.objects.filter(registered_dttm__date=datetime.date(now- timedelta(1)).isoformat()).aggregate(Sum('total_time'))
    yesterday_values=yesterday_filter.values()

    for i in yesterday_values:
        yesterday_values = i

    if yesterday_values==None:
        yesterday_values=0

    gap_time=t_value_sec-yesterday_values
    gap_time_signed=gap_time


    gap_time=abs(gap_time)
    hours_gap = gap_time // 3600
    gap_time = gap_time - hours*3600
    mu_gap = gap_time // 60
    ss_gap = gap_time - mu*60

    if hours_gap==0 and mu_gap==0:
        if gap_time_signed <0:
            gap_time='-'+str(gap_time)+'초'
        else:
            gap_time='+'+str(gap_time)+'초'
    elif hours_gap==0 and mu_gap!=0:
        if gap_time_signed <0:
            gap_time='-'+str(mu_gap)+'분'
        else:
            gap_time='+'+str(mu_gap)+'분'
    elif hours_gap!=0:
        if gap_time_signed <0:
            gap_time='-'+str(hours_gap)+'시간'
        else:
            gap_time='+'+str(hours_gap)+'시간'


    # 그래프(운동 시간으로 나타냄)
    today_data=Data.objects.filter(registered_dttm__date=datetime.date(now).isoformat()).all()
    today_data_values=today_data.values()
    
    graph_data={}
    graph_data_list=[]
    for i in today_data_values:
        a=datetime.time(i["registered_dttm"]).hour
        start=0
        end=3
        for j in range(8):
            if a>=start and a<end:
                if str(start) not in graph_data:
                    graph_data[str(start)]={"x": str(start)+"시", "y": i["total_time"]}
                else:
                    graph_data[str(start)]["y"]+=i["total_time"]
            start+=3
            end+=3

    for i in graph_data.values():
        graph_data_list.append(i)
    
    # 운동한 영상별 유사도
    results = Data.objects.filter(registered_dttm__date=datetime.date(now).isoformat()).order_by('registered_dttm')
    result_values=list(results.values())

    num=1
    for i in range(0, len(result_values)):
        result_values[i]["id"]=num
        num+=1

    context = {
        'hours': hours,
        'mu': mu,
        'ss': ss,
        'video_cnt': video_cnt,
        'gap_time':gap_time,
        'graph_data':graph_data_list,
        'results':result_values
    }

    return render(request, 'day.html', context)


def week(request):
    def AddDays(sourceDate, count): 
            targetDate = sourceDate + timedelta(days = count) 
            return targetDate 
    def GetWeekFirstDate(sourceDate): 
        temporaryDate =datetime(sourceDate.year, sourceDate.month, sourceDate.day) 
        weekDayCount = temporaryDate.weekday() 
        targetDate = AddDays(temporaryDate, -weekDayCount); 
        return targetDate

    start_date=GetWeekFirstDate(datetime.date(datetime.now()))

    # 총 운동 시간
    #time_sum = Data.objects.aggregate(Sum('total_time'))
    time_filter=Data.objects.filter(registered_dttm__range=[datetime.date(start_date),datetime.date(start_date)+timedelta(6)]).aggregate(Sum('total_time'))

    #t_values = time_sum.values()
    t_values=time_filter.values()

    for i in t_values:
        t_values = i

    t_value_sec=t_values

    hours = t_values // 3600
    t_values = t_values - hours*3600
    mu = t_values // 60
    ss = t_values - mu*60
    #print(hours, '시간', mu, '분', ss, '초')

    # 운동한 영상
    #video = Data.objects.annotate(Count('videoId'))
    video = Data.objects.filter(registered_dttm__range=[start_date,start_date+timedelta(6)]).annotate(Count('videoId'))
    v_values = list(video.values_list('videoId'))
    video_cnt = len(v_values)
    #print(video_cnt)

    # 전주 대비 운동량
    lastWeek_start_date=GetWeekFirstDate(datetime.date(start_date-timedelta(1)))
    lastWeek_filter=Data.objects.filter(registered_dttm__range=[lastWeek_start_date,datetime.date(start_date)+timedelta(6)]).aggregate(Sum('total_time'))
    lastWeek_values=lastWeek_filter.values()

    for i in lastWeek_values:
        lastWeek_values = i

    if lastWeek_values==None:
        lastWeek_values=0

    gap_time=t_value_sec-lastWeek_values
    gap_time_signed=gap_time


    gap_time=abs(gap_time)
    hours_gap = gap_time // 3600
    gap_time = gap_time - hours*3600
    mu_gap = gap_time // 60
    ss_gap = gap_time - mu*60

    if hours_gap==0 and mu_gap==0:
        if gap_time_signed <0:
            gap_time='-'+str(gap_time)+'초'
        else:
            gap_time='+'+str(gap_time)+'초'
    elif hours_gap==0 and mu_gap!=0:
        if gap_time_signed <0:
            gap_time='-'+str(mu_gap)+'분'
        else:
            gap_time='+'+str(mu_gap)+'분'
    elif hours_gap!=0:
        if gap_time_signed <0:
            gap_time='-'+str(hours_gap)+'시간'
        else:
            gap_time='+'+str(hours_gap)+'시간'


    # 그래프(운동 시간으로 나타냄)
    #t_day = Data.objects.values('total_time')
    today_data=Data.objects.filter(registered_dttm__date=datetime.date(datetime.now()).isoformat()).all()
    today_data_values=today_data.values()
    graph_data={}
    graph_data_list=[]
    index=[0,]
    for i in today_data_values:
        a=datetime.time(i["registered_dttm"]).hour
        start=0
        end=3
        for j in range(8):
            if a>=start and a<end:
                if str(start) not in graph_data:
                    graph_data[str(start)]={"x": str(start)+"시", "y": i["total_time"]}
                else:
                    graph_data[str(start)]["y"]+=i["total_time"]
                start+=3
                end+=3
    for i in graph_data.values():
        graph_data_list.append(i)

    results = Data.objects.filter(registered_dttm__range=[datetime.date(start_date),datetime.date(start_date)+timedelta(6)]).order_by('registered_dttm')
    result_values=list(results.values())

    num=1
    for i in range(0, len(result_values)):
        result_values[i]["id"]=num
        num+=1

    context = {
        'hours': hours,
        'mu': mu,
        'ss': ss,
        'video_cnt': video_cnt,
        'gap_time':gap_time,
        'graph_data':graph_data_list,
        'results':result_values

    }

    return render(request, 'week.html',context)

def month(request):
    return render(request, 'month.html')

def subYtbchn(request):
    return render(request, 'subYtbchn.html')

def wholebody(request):
    videos=[]
    if request.method=='GET':
        search_url = 'https://youtube.googleapis.com/youtube/v3/search'
        video_url = 'https://youtube.googleapis.com/youtube/v3/videos'

        search_params = {
            'part' : 'snippet',
            'q' : request.GET['part']+'운동',
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
        
    return render(request, 'wholebody.html',context)

def smartmode(request):
    if request.method=='GET':
        url=request.GET
        video = pafy.new(url['cmd'])
        channel_id=url['channel']
        best = video.getbest(preftype="mp4")

        re_result = re.search('https\:\/\/www\.youtube\.com\/watch\?v\=(\S+)',url['cmd'])
        global video_id
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

        global v_data
        v_data={'video_address': best.url,
                'video_id':video_id,
                'url':url['cmd'],
                'title':snippet['title'],
                'publishedAt':publishedAt_result.group(0),
                'viewCount':statistics['viewCount'],
                'tags':tags_rand[0],
                'channelId':channel_id,
            }

    if request.method == "POST":
        videoId = video_id   #딕셔너리형태
        high = request.POST.get('high',None)
        low = request.POST.get('low',None)
        average = request.POST.get('average',None)

        high_img_route = "C:/Users/서유림/Documents/GitHub/Fitner_Web/workspace/yoorim/fitnerproject/fitnerapp/static/resulthigh.png"
        low_img_route = "C:/Users/서유림/Documents/GitHub/Fitner_Web/workspace/yoorim/fitnerproject/fitnerapp/static/result/low.png"

        high_start_section = request.POST.get('high_start_section',None)
        high_end_section = request.POST.get('high_end_section',None)
        low_start_section = request.POST.get('low_start_section',None)
        low_end_section = request.POST.get('low_end_section',None)
        total_time = request.POST.get('total_time',None)

        data = Data(
                videoId=videoId, high=high, low=low, average=average, high_img_route=high_img_route,
                low_img_route=low_img_route, high_start_section=high_start_section, high_end_section=high_end_section,
                low_start_section=low_start_section, low_end_section=low_end_section, total_time=total_time
        )
        data.save()
    
    if request.method == "POST":
        username = request.POST.get('username',None)   #딕셔너리형태
        userphone = request.POST.get('userphone',None)
        similarity = request.POST.get('similarity',None)
        if username and userphone :
            ranking = Ranking(username=username, userphone=userphone, similarity=similarity)
            ranking.save()
            #return redirect('smartmode')

    return render(request, 'smartmode.html', v_data)

@csrf_exempt
def videoplayer(request):
    videos=[]
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
        search_url='https://www.googleapis.com/youtube/v3/search'

        #=============================================================video===============================
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

        #=============================================================channel===============================
        channelTitle=snippet["channelTitle"]

        channel_params={
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part':"statistics,snippet",
            'id':channel_id
        }

        channel_r=requests.get(channel_url, params=channel_params)
        #print(channel_r.json())
        channel_result=channel_r.json()['items'][0]
        #print(channel_result['snippet']['thumbnails']['default']['url'])
        rankings_values=list(rankings.values())

        #=============================================================search===============================
        search_params = {
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part' : 'snippet',
            'type':'video',
            'relatedToVideoId' : video_id,
            'maxResults':10,
            'videoLicense' : 'creativeCommon'
        }
        search_r=requests.get(search_url, params=search_params)
        search_results=search_r.json()['items']

        video_ids = []
        for result in search_results:
            video_ids.append(result['id']['videoId'])
        
        for result in search_results:
            #print(result)
            #print(videos)
            try:
                video_data = {
                    'title' : result['snippet']['title'],
                    'id' : result['id'],
                    'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
                    'thumbnail' : result['snippet']['thumbnails']['high']['url'],
                    'channelTitle' : result['snippet']['channelTitle'],
                    'channel_id':result['snippet']['channelId']
                }
                videos.append(video_data)
            except KeyError :
                pass

        #=================================================================================================
        num=1
        for i in range(0,len(rankings_values)):
            rankings_values[i]["id"]=num
            num+=1

        #print(rankings_values)
        data={ 'video_address': best.url,
                'url':url['cmd'],
                'rankings':rankings_values,
                'title':snippet['title'],
                'publishedAt':publishedAt_result.group(0),
                'viewCount':statistics['viewCount'],
                'tags':tags_rand[0],
                'channelTitle':channelTitle,
                'channelImage':channel_result['snippet']['thumbnails']['default']['url'],
                'channelSubscriber':channel_result['statistics']['subscriberCount'],
                'channelId':channel_id,
                'videos':videos[:8],
             }

    return render(request, 'videoplayer.html', data)

def ytbchannel(request):
    videos = []
    if request.method == "GET":
        data=request.GET
        channel_id=data['channelId']
        channel_url='https://youtube.googleapis.com/youtube/v3/channels'
        playlist_url='https://www.googleapis.com/youtube/v3/playlistItems'
        video_url = 'https://youtube.googleapis.com/youtube/v3/videos'

        channel_params={
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part':"statistics,snippet,contentDetails",
            'id':channel_id
        }

        channel_r=requests.get(channel_url, params=channel_params)
        channel_result=channel_r.json()['items'][0]
        #print(channel_r.json())
        playlist_id=channel_result["contentDetails"]["relatedPlaylists"]["uploads"]
        playlist_params={
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part':"snippet,contentDetails",
            'playlistId':playlist_id,
            'maxResults':16
        }

    
        playlist_r=requests.get(playlist_url, params=playlist_params)
        playlist_results=playlist_r.json()['items']

        video_ids = []
        for result in playlist_results:
            video_ids.append(result['contentDetails']['videoId'])


        video_params = {
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part' : 'statistics',
            'id' : ','.join(video_ids),
            'maxResults' : 1
        }

        video_r = requests.get(video_url, params=video_params)

        video_results = video_r.json()['items']



        for result in playlist_results:
            pre_publishedAt=result["snippet"]['publishedAt']
            publishedAt_result = re.search('(\d+)\-(\d+)\-(\d+)',pre_publishedAt)
            video_data = {
                'title' : result['snippet']['title'],
                'id' : result['contentDetails']["videoId"],
                'url' : 'https://www.youtube.com/watch?v='+result['contentDetails']["videoId"],
                #'duration' : int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                'thumbnail' : result['snippet']['thumbnails']['high']['url'],
                'channelTitle' : result['snippet']['channelTitle'],
                # 'publishedAt' : result['snippet']['publishedAt'],
                'publishedAt':publishedAt_result.group(0),
                #'channel_id':result['snippet']['channelId']
                
            }

            videos.append(video_data)

        viewCounts=[]
        for result in video_results:
            viewCounts.append(result['statistics']['viewCount'])

        for i in range(0,len(viewCounts)):
            videos[i]["viewCount"]=viewCounts[i]

        context={
                'channelTitle':channel_result['snippet']['title'],
                'channelImage':channel_result['snippet']['thumbnails']['default']['url'],
                'channelSubscriber':channel_result['statistics']['subscriberCount'],
                'channelId':channel_id,
                'videos':videos,
             }


    return render(request, 'ytbchannel.html',context)

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