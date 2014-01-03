from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^home/$', 'landing.views.home', name='landing_home'),

)
