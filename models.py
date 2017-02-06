# -*- encoding:utf-8 -*-
from django.db import models

# Create your models here.

#maven编译使用的配置表
class Profiles(models.Model):
    P = models.CharField(max_length=20)
    add_date = models.DateTimeField('date published')

    def __unicode__(self):
        return self.P


#管理webents的表，记录webent上次发版的时间以及上次发版使用的配置
class Webents(models.Model):
    name= models.CharField(max_length=50)
    lastPubStatus=models.ForeignKey(Profiles,default=1)
    lastPubDate=models.DateTimeField('date published')
    add_date = models.DateTimeField('date published')

    def __unicode__(self):
        return self.name


#author提交人，message提交备注，commitsFile修改文件，git提交的nvalue唯一号
class Commits(models.Model):
    author= models.CharField(max_length=20)
    message = models.CharField(max_length=1000)
    commitsFile = models.CharField(max_length=2000)
    nvalue=models.CharField(max_length=2000)
    commit_date = models.DateTimeField(default='2015-01-01 10:37:54')

