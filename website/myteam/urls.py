from django.conf.urls.defaults import *

urlpatterns = patterns('myteam.views',
    (r'^$', 'index'),
    (r'^calendar/$', 'update_calendar'),
)
