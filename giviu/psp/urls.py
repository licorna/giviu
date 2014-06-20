from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^pay$', 'psp.views.first_stage', name='psp_first'),
                       url(r'^success/(?P<token>\S+)$', 'psp.views.pp_response_success',
                           name='psp_success'),
                       url(r'^error/(?P<token>\S+)$', 'psp.views.pp_response_error',
                           name='psp_error'))
