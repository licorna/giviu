from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'status.views.status', name='status'),
    url(r'^version$', 'status.views.version', name='version'),
)
