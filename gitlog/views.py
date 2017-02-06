from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Commits, Profiles, Webents
from django.shortcuts import  get_object_or_404, render, render_to_response
from django.core.urlresolvers import reverse
from django.views import generic
import time,datetime

from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
from pygit2 import Repository
from pygit2 import GIT_SORT_NONE,GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE,GIT_SORT_TIME
import mysql.connector



class GetloglView(generic.ListView):
    model = Commits
    template_name = 'gitlog/viewlog.html'



class UpdatelogView(generic.ListView):
    model = Commits
    template_name = 'gitlog/Updatelog.html'



class PubsitesView(generic.ListView):
    model = Webents
    template_name = 'gitlog/Pubsites.html'
#
# def Updatelog(request):
cnx = mysql.connector.connect(user='root',password='yb198697',host='127.0.0.1',database='gitlog')
argslog=[]
cursor = cnx.cursor()
# cursor.execute("SELECT UNIX_TIMESTAMP(date) FROM gitlog.gitlog order by gitlog.date desc limit 1")
# for (datetimelog) in cursor:
#     dataNewtime= datetimelog[0]
#
# repo = Repository('/home/chaosbom/git/ArhasMK/.git')
#
# for commit in repo.walk(repo.head.target,GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):
#
#     if(commit.author.time > dataNewtime):
#         print commit.author.time, dataNewtime, commit.author.time > dataNewtime, commit.author.time - dataNewtime
#         logtmp=[]
#         logtmp.append(commit.tree.id.hex)
#         logtmp.append(commit.message)
#         logtmp.append(datetime.datetime.utcfromtimestamp(commit.author.time))
#         logtmp.append(commit.author.name)
#         print(logtmp)
#         argslog.append(logtmp)
#         log=(commit.tree.id.hex,commit.message,datetime.datetime.utcfromtimestamp(commit.author.time).strftime("%Y-%m-%d %H:%M:%S"),commit.author.name)
#         add_log="INSERT INTO gitlog.gitlog (nvalue,comments,date,Author) VALUES (%s,%s,%s,%s)"
#         cursor.executemany(add_log, argslog)
# cursor.close()


def Updatelog(request):
    argslog = []
    repo = Repository('/home/chaosbom/git/ArhasMK/.git')

    for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):
        logtmp = []
        i =Commits(author=commit.author.name,message=commit.message,commitsFile='',nvalue=commit.tree.id.hex,
                   commit_date=datetime.datetime.utcfromtimestamp(commit.author.time))
        i.save()
    return HttpResponse("success!")

def getlogbyPage(request):
    after_range_num = 5
    before_range_num = 4
    try:
        page = int(request.GET.get('page', '1'))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    Commts_list = Commits.objects.all().order_by('-id')
    paginator = Paginator(Commts_list, 10)
    try:
        Commtslist = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        Commtslist = paginator.page(1)
    if page >= after_range_num:
        page_range = paginator.page_range[page - after_range_num:page + before_range_num]
    else:
        page_range = paginator.page_range[0:int(page) + before_range_num]
    return render_to_response('gitlog/viewlog.html', locals())

#def pubsites(request,webentsChoose):
