from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^login/$', 'merchant.views.do_login', name='login_merchant'),
    url(r'^home/$', 'merchant.views.home', name='home'),
    url(r'^validate/$', 'merchant.views.validate', name='validate'),
    url(r'^customers/$', 'merchant.views.customers', name='customers'),
    url(r'^customer/profile/(?P<customer_id>\d+)$', 'merchant.views.customer_profile', name='customer_profile'),
    url(r'^customer/edit/(?P<customer_id>\d+)$', 'merchant.views.customer_edit', name='customer_edit'),
)
