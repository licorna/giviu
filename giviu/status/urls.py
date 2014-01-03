from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^', 'status.views.index', name='status'),
)
