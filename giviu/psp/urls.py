from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^pay$', 'psp.views.first_stage', name='psp_first'),
                       url(r'^success/(?P<token>\S+)$', 'psp.views.pp_response', {'status':'success'}, name='psp_success'),
                       url(r'^success_prueba$', 'psp.views.prueba', name='prueba'),
                       url(r'^error/(?P<token>\S+)$', 'psp.views.pp_response', {'status':'error'}, name='psp_error'),
)
