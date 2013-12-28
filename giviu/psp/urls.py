from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^pay$', 'psp.views.first_stage', name='psp_first'),
)
