from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^pay$', 'psp.views.first_stage', name='psp_first'),
                       url(r'^success/(?P<token>\S+)$', 'psp.views.success', name='psp_success'),
)
