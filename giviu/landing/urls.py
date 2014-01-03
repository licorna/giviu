from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^home/$',
                           'landing.views.home',
                           name='landing_home'))
