from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^$',
                           'login.views.login',
                          name='base_login'),

                       url(r'^register/$',
                           'login.views.email_register',
                           name='email_register'),

                       url(r'^validate/(?P<token>[0-9a-z]+)$',
                           'login.views.email_validate',
                           name='email_validate'),

)
