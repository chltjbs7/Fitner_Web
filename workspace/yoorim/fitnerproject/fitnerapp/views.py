import requests
import pafy
import re
import random
import pandas

from collections import Counter
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from .models import User
from django.contrib.auth.models import User
from django.contrib import auth
from .models import Rank
from django.views.decorators.http import condition
from .models import Data
from django.db.models import Sum
from django.db.models import Count

# Create your views here.

def home(request):
    return render(request, 'home.html')

def showRanking(request):
    rankings = Rank.objects.all().order_by('-similarity')[:5]
    rankings_values=list(rankings.values())
    num=1
    for i in range(0,len(rankings_values)):
        rankings_values[i]["id"]=num
        num+=1

    context = {
        'rankings':rankings_values,
    }
    return render(request, 'showRanking.html', context)

def allViewRecord(request):
    return render(request, 'allViewRecord.html')

def playlist(request):
    return render(request, 'playlist.html')

def barChart(request):
#     labels = []
#     data = []

#     # 그래프(운동 시간으로 나타냄)
#     #t_day = Data.objects.values('total_time')
#     today_data=Data.objects.filter(registered_dttm__date=datetime.date(datetime.now()).isoformat()).all()
#     today_data_values=today_data.values()
#     graph_data={}
#     graph_data_list=[]
#     index=[0,]
#     for i in today_data_values:
#         a=datetime.time(i["registered_dttm"]).hour
#         start=0
#         end=3
#         for j in range(8):
#             if a>=start and a<end:
#                 if str(start) not in graph_data:
#                     graph_data[str(start)]={"x": str(start)+"시", "y": i["total_time"]}
#                 else:
#                     graph_data[str(start)]["y"]+=i["total_time"]
#                 start+=3
#                 end+=3
#     for i in graph_data.values():
#         graph_data_list.append(i)

    
#     return render(request, 'barChart.html', {
#         'graph_data':graph_data_list
#     })
    return render(request, 'barChart.html')

def day(request):
    if request.method=='GET':
        r=request.GET
        try:
            today = r['today']
            part=today[-4:]
            if part=='left':
                today=today[:-4]
                now=datetime.strptime(today,"%Y-%m-%d")-timedelta(1)
            else:
                now=datetime.strptime(today,"%Y-%m-%d")+timedelta(1)
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
    
    if(t_values==None):
        t_values=0

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
        graph_data_list.append({"x": str(a)+"시", "y": i["total_time"]})
    
    # 운동한 영상별 유사도
    results = Data.objects.filter(registered_dttm__date=datetime.date(now).isoformat()).order_by('-registered_dttm')

    result_values=list(results.values())
    video_ids=[]
    for i in result_values:
        video_ids.append(i['videoId'])

    # 모달창 썸네일,비디오 이름
    video_url = 'https://youtube.googleapis.com/youtube/v3/videos'
    video_params = {
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part' : 'snippet',
            'id' : video_ids,
    }
    video_r=requests.get(video_url,params=video_params)
    video_results=video_r.json()['items']

    for i in result_values:
        index=0
        i['channelTitle']=video_results[index]['snippet']['channelTitle']
        i['video_title']=video_results[index]['snippet']['title']
        i['video_thumbnail']=video_results[index]['snippet']['thumbnails']['high']['url']
        index+=1

    context = {
        'today':str(now.strftime("%Y-%m-%d")),
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
    if request.method=='GET':
        r=request.GET

        try:
            today = r['today']
            part=today[-4:]
            if part=='left':
                today=today[:-4]
                now=datetime.strptime(today,"%Y-%m-%d")-timedelta(1)
            else:
                now=datetime.strptime(today,"%Y-%m-%d")+timedelta(1)
        except:
            now=datetime.now()

    def AddDays(sourceDate, count): 
            targetDate = sourceDate + timedelta(days = count) 
            return targetDate 
    def GetWeekFirstDate(sourceDate): 
        temporaryDate =datetime(sourceDate.year, sourceDate.month, sourceDate.day) 
        weekDayCount = temporaryDate.weekday() 
        targetDate = AddDays(temporaryDate, -weekDayCount); 
        return targetDate

    start_date=GetWeekFirstDate(datetime.date(now))

    # 총 운동 시간
    #time_sum = Data.objects.aggregate(Sum('total_time'))
    time_filter=Data.objects.filter(registered_dttm__range=[datetime.date(start_date),datetime.date(start_date)+timedelta(6)]).aggregate(Sum('total_time'))

    #t_values = time_sum.values()
    t_values=time_filter.values()

    for i in t_values:
        t_values = i

    if(t_values==None):
        t_values=0

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
    lastWeek_filter=Data.objects.filter(registered_dttm__range=[lastWeek_start_date,datetime.date(lastWeek_start_date)+timedelta(6)]).aggregate(Sum('total_time'))
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
    week_filter=Data.objects.filter(registered_dttm__range=[datetime.date(start_date),datetime.date(start_date)+timedelta(6)])
    week_data_values=week_filter.values()
    
    #print(week_data_values)
    tmp_week_graph=[]
    for i in week_data_values:
        a=datetime.date(i["registered_dttm"]).weekday()
        if a==0:
            tmp_week_graph.append({'월':i["total_time"]})
        elif a==1:
            tmp_week_graph.append({'화':i["total_time"]})
        elif a==2:
            tmp_week_graph.append({'수':i["total_time"]})
        elif a==3:
            tmp_week_graph.append({'목':i["total_time"]})
        elif a==4:
            tmp_week_graph.append({'금':i["total_time"]})
        elif a==5:
            tmp_week_graph.appen({'토':i["total_time"]})
        elif a==6:
            tmp_week_graph.append({'일':i["total_time"]})
    
    # for i in tmp_week_graph:
    #         print(i)

    tmp_total_graph_data=[]
    try:
        sum_graph_data=Counter(tmp_week_graph[0])
        total_graph_data=[]
        for i in range(1,len(tmp_week_graph)):
            sum_graph_data=sum_graph_data+Counter(tmp_week_graph[i])
        sum_graph_data_dict=dict(sum_graph_data)
        for j in range(len(sum_graph_data_dict)):
            keys=list(sum_graph_data_dict.keys())
            values=list(sum_graph_data_dict.values())
            total_graph_data.append({'x':keys[j],'y':values[j]})
    except IndexError:
        total_graph_data=[]

    # 운동한 영상별 유사도
    results = Data.objects.filter(registered_dttm__date=datetime.date(now).isoformat()).order_by('-registered_dttm')

    result_values=list(results.values())
    video_ids=[]
    for i in result_values:
        video_ids.append(i['videoId'])

    # 모달창 썸네일,비디오 이름
    video_url = 'https://youtube.googleapis.com/youtube/v3/videos'
    video_params = {
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part' : 'snippet',
            'id' : video_ids,
    }
    video_r=requests.get(video_url,params=video_params)
    video_results=video_r.json()['items']

    for i in result_values:
        index=0
        i['channelTitle']=video_results[index]['snippet']['channelTitle']
        i['video_title']=video_results[index]['snippet']['title']
        i['video_thumbnail']=video_results[index]['snippet']['thumbnails']['high']['url']
        index+=1

    context = {
        'today':str(now.strftime("%Y-%m-%d")),
        'hours': hours,
        'mu': mu,
        'ss': ss,
        'video_cnt': video_cnt,
        'gap_time':gap_time,
        'graph_data':total_graph_data,
        'results':result_values
    }

    return render(request, 'week.html',context)

def month(request):
    if request.method=='GET':
        r=request.GET
        try:
            today = r['today']
            part=today[-4:]
            if part=='left':
                today=today[:-4]
                now=datetime.strptime(today,"%Y-%m-%d")-timedelta(1)
            else:
                now=datetime.strptime(today,"%Y-%m-%d")+timedelta(1)
        except:
            now=datetime.now()
    
    # 총 운동 시간
    #time_sum = Data.objects.aggregate(Sum('total_time'))
    time_filter=Data.objects.filter(registered_dttm__month=now.month).aggregate(Sum('total_time'))
    
    #t_values = time_sum.values()
    t_values=time_filter.values()

    for i in t_values:
        t_values = i

    if(t_values==None):
        t_values=0

    t_value_sec=t_values

    hours = t_values // 3600
    t_values = t_values - hours*3600
    mu = t_values // 60
    ss = t_values - mu*60
    #print(hours, '시간', mu, '분', ss, '초')

    # 운동한 영상
    #video = Data.objects.annotate(Count('videoId'))
    video = Data.objects.filter(registered_dttm__month=now.month).annotate(Count('videoId'))
    v_values = list(video.values_list('videoId'))
    video_cnt = len(v_values)
    #print(video_cnt)

    # 전날 대비 운동량
    yesterday_filter=Data.objects.filter(registered_dttm__month=now.month-1).aggregate(Sum('total_time'))
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
    #t_day = Data.objects.values('total_time')
    #매월 마지막날 구하기
    def IsLeapYear(year): 
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0): 
            return True 
        else: 
            return False 
    MonthDayCountList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] 
    def GetMonthLastDate(sourceDate): 
        dayCount = MonthDayCountList[sourceDate.month - 1] 
        if sourceDate.month == 2: 
            if IsLeapYear(sourceDate.year): 
                dayCount += 1 
        targetDate =datetime(sourceDate.year, sourceDate.month, dayCount) 
        return targetDate 

    #매월 첫째날
    first_day = now.replace(day=1)
    last_day=GetMonthLastDate(now)

    #총 날짜
    month_label=[]
    dt_index = pandas.date_range(start=datetime.date(first_day), end=datetime.date(last_day))
    for time in dt_index:
        month_label.append(time.strftime("%m-%d"))

    
    month_data=Data.objects.filter(registered_dttm__month=now.month).all()
    month_data_values=month_data.values()

    
    tmp_graph_data_list=[]
    for i in month_data_values:
        tmp_graph_data_list.append({i['registered_dttm'].strftime("%Y-%m-%d"):i['total_time']})
    

    try:
        sum_graph_data=Counter(tmp_graph_data_list[0])
        total_graph_data=[]
        for i in range(1,len(tmp_graph_data_list)):
            sum_graph_data=sum_graph_data+Counter(tmp_graph_data_list[i])
        sum_graph_data_dict=dict(sum_graph_data)
        for j in range(len(sum_graph_data_dict)):
            keys=list(sum_graph_data_dict.keys())
            values=list(sum_graph_data_dict.values())
            total_graph_data.append({'x':keys[j][5:],'y':values[j]})
    except IndexError :
        total_graph_data=[]

    # 운동한 영상별 유사도
    results = Data.objects.filter(registered_dttm__date=datetime.date(now).isoformat()).order_by('-registered_dttm')

    result_values=list(results.values())
    video_ids=[]
    for i in result_values:
        video_ids.append(i['videoId'])

    # 모달창 썸네일,비디오 이름
    video_url = 'https://youtube.googleapis.com/youtube/v3/videos'
    video_params = {
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part' : 'snippet',
            'id' : video_ids,
    }
    video_r=requests.get(video_url,params=video_params)
    video_results=video_r.json()['items']

    for i in result_values:
        index=0
        i['channelTitle']=video_results[index]['snippet']['channelTitle']
        i['video_title']=video_results[index]['snippet']['title']
        i['video_thumbnail']=video_results[index]['snippet']['thumbnails']['high']['url']
        index+=1

    context = {
        'today':str(now.strftime("%Y-%m-%d")),
        'hours': hours,
        'mu': mu,
        'ss': ss,
        'video_cnt': video_cnt,
        'gap_time':gap_time,
        'month_label':month_label,
        'graph_data':total_graph_data,
        'results':result_values
    }

    return render(request, 'month.html',context)

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
        high_img_name = request.POST.get('high_img_name',None)
        low_img_name = request.POST.get('low_img_name',None)
        high_start_section = request.POST.get('high_start_section',None)
        high_end_section = request.POST.get('high_end_section',None)
        low_start_section = request.POST.get('low_start_section',None)
        low_end_section = request.POST.get('low_end_section',None)
        total_time = request.POST.get('total_time',None)

        data = Data(
                videoId=videoId, high=high, low=low, average=average,
                high_img_name=high_img_name, low_img_name=low_img_name,
                high_start_section=high_start_section, high_end_section=high_end_section,
                low_start_section=low_start_section, low_end_section=low_end_section,
                total_time=total_time
        )
        data.save()
    
    if request.method == "POST":
        username = request.POST.get('username',None)   #딕셔너리형태
        userphone = request.POST.get('userphone',None)
        similarity = request.POST.get('similarity',None)
        if username and userphone :
            ranking = Rank(username=username, userphone=userphone, similarity=similarity)
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

        rankings = Rank.objects.all().order_by('-similarity')[:5]

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
        channel_url='https://youtube.googleapis.com/youtube/v3/channels'

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

        channel_ids=[]
        for result in results:
            channel_ids.append(result['snippet']['channelId'])

        video_params = {
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part' : 'snippet,contentDetails,statistics',
            'id' : ','.join(video_ids),
            'maxResults' : 1
        }

        r = requests.get(video_url, params=video_params)

        results = r.json()['items']

        channel_params={
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part':"snippet",
            'id':channel_ids
        }

        channel_imgs=[]
        channel_r = requests.get(channel_url, params=channel_params)

        channel_results = channel_r.json()['items']
        for i in channel_results:
            channel_imgs.append(i['snippet']['thumbnails']['default']['url'])
        
        for result in results:
            channel_img_index=0
            video_data = {
                'title' : result['snippet']['title'],
                'id' : result['id'],
                'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
                'thumbnail' : result['snippet']['thumbnails']['high']['url'],
                'channelTitle' : result['snippet']['channelTitle'],
                'publishedAt':publishedAt_result.group(0),
                'viewCount' : result['statistics']['viewCount'],
                'channel_id':result['snippet']['channelId'],
                'channel_img':channel_imgs[channel_img_index]
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