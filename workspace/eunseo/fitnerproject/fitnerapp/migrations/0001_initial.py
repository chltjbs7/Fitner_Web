# Generated by Django 3.1.7 on 2021-05-18 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('videoId', models.CharField(max_length=10, verbose_name='영상 Id')),
                ('high', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='최고 유사도')),
                ('low', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='최저 유사도')),
                ('average', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='평균 유사도')),
                ('high_img_route', models.CharField(max_length=256, verbose_name='최고 유사도 이미지 경로')),
                ('low_img_route', models.CharField(max_length=256, verbose_name='최저 유사도 이미지 경로')),
                ('high_start_section', models.IntegerField(verbose_name='최고 유사도 영상 시작 구간')),
                ('high_end_section', models.IntegerField(verbose_name='최고 유사도 영상 끝 구간')),
                ('low_start_section', models.IntegerField(verbose_name='최저 유사도 영상 시작 구간')),
                ('low_end_section', models.IntegerField(verbose_name='최저 유사도 영상 끝 구간')),
                ('total_time', models.IntegerField(default=0, verbose_name='운동시간')),
                ('registered_dttm', models.DateTimeField(auto_now_add=True, verbose_name='등록시간')),
            ],
            options={
                'db_table': 'data',
            },
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('videoName', models.CharField(max_length=256, verbose_name='재생목록 이름')),
                ('videoId', models.CharField(max_length=256, verbose_name='영상 Id')),
                ('registered_dttm', models.DateTimeField(auto_now_add=True, verbose_name='등록시간')),
            ],
            options={
                'db_table': 'playlist',
            },
        ),
        migrations.CreateModel(
            name='Ranking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=10, verbose_name='이름')),
                ('userphone', models.CharField(max_length=11, verbose_name='전화번호')),
                ('similarity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='유사도')),
                ('registered_dttm', models.DateTimeField(auto_now_add=True, verbose_name='등록시간')),
            ],
            options={
                'db_table': 'ranking',
            },
        ),
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channelId', models.CharField(max_length=256, verbose_name='채널 Id')),
                ('registered_dttm', models.DateTimeField(auto_now_add=True, verbose_name='등록시간')),
            ],
            options={
                'db_table': 'subscribe',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=64, verbose_name='사용자명')),
                ('password', models.CharField(max_length=64, verbose_name='비밀번호')),
                ('registered_dttm', models.DateTimeField(auto_now_add=True, verbose_name='등록시간')),
            ],
            options={
                'db_table': 'test_user',
            },
        ),
    ]
