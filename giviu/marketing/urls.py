from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^daily-nl$', 'marketing.views.daily_nl',
                           name='marketing_daily_nl'),
)
