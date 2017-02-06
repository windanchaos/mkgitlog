
import django,os,sys
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mydemo.settings")
django.setup()

from django.test import TestCase
from gitlog.models import Commits

obj = Commits.objects.all().filter(author='雅鱼(王宇)')
for e in obj:
    print(e.author,e.message,e.commit_date)


# Create your tests here.
