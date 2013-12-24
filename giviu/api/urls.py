from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^version$', 'api.views.version', name='api_version'),
    url(r'^users/exists-by-fb/(?P<fbid>\d+)$', 'api.views.user_exists_by_fbid', name='api_users_exists_by_fb'),

)
