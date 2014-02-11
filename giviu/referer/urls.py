from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^(?P<code>[a-z0-9-]+)',
                           'referer.views.friend',
                           name='referer_code'))
