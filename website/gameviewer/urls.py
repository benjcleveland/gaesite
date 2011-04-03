from django.conf.urls.defaults import *

urlpatterns = patterns('gameviewer.views',
    (r'^$', 'index'),
    (r'^(?P<game_id>\d+)/$', 'detail'),
    (r'^list/(?P<game_id>\d+)/(?P<search>\w+)/$', 'list'),
    (r'^rate/(?P<game_id>\d+)/$', 'rate'),
    (r'^about/$', 'about'),
    (r'^top/$', 'top'),
    (r'^usertop/$', 'user_top'),
)
