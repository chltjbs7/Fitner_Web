from django.db import models

# Create your models here.

class User(models.Model): #장고에서 제공하는 models.Model를 상속받아야한다.
    username = models.CharField(max_length=64,verbose_name = '사용자명')
    password = models.CharField(max_length=64,verbose_name = '비밀번호')
    registered_dttm = models.DateTimeField(auto_now_add=True,verbose_name='등록시간') 
    #저장되는 시점의 시간을 자동으로 삽입해준다.

    def __str__(self): # 이 함수 추가
        return self.username  # User object 대신 나타낼 문자

    class Meta: #메타 클래스를 이용하여 테이블명 지정
        db_table = 'test_user'

class Ranking(models.Model):
    username = models.CharField(max_length=10,verbose_name = '이름')
    userphone = models.CharField(max_length=11,verbose_name = '전화번호')
    similarity = models.CharField(max_length=10,verbose_name = '유사도')
    registered_dttm = models.DateTimeField(auto_now_add=True,verbose_name='등록시간') 

    def __str__(self):
        return self.username
 
    class Meta:
        db_table = 'ranking'

class Data(models.Model):
    videoId = models.CharField(max_length=10,verbose_name = '영상 Id')
    high = models.CharField(max_length=10,verbose_name = '최고 유사도')
    low = models.CharField(max_length=10,verbose_name = '최저 유사도')
    average = models.CharField(max_length=10,verbose_name = '평균 유사도')
    high_img_route = models.CharField(max_length=256,verbose_name = '최고 유사도 이미지 경로')
    low_img_route = models.CharField(max_length=256,verbose_name = '최저 유사도 이미지 경로')
    high_start_section = models.CharField(max_length=64,verbose_name = '최고 유사도 영상 시작 구간')
    high_end_section = models.CharField(max_length=64,verbose_name = '최고 유사도 영상 끝 구간')
    low_start_section = models.CharField(max_length=64,verbose_name = '최저 유사도 영상 시작 구간')
    low_end_section = models.CharField(max_length=64,verbose_name = '최저 유사도 영상 끝 구간')
    total_time = models.CharField(max_length=64,verbose_name = '운동시간')
    registered_dttm = models.DateTimeField(auto_now_add=True,verbose_name='등록시간')

    def __str__(self):
        return self.videoId
 
    class Meta:
        db_table = 'data'