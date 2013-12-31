from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^login/$', 'merchant.views.login', name='login_merchant'),
    url(r'^home/$', 'merchant.views.home', name='home'),
    url(r'^validate/$', 'merchant.views.validate', name='validate'),
    url(r'^customers/$', 'merchant.views.customers', name='customers'),
    url(r'^customer/profile/$', 'merchant.views.customer_profile', name='customer_profile'),
    url(r'^customer/edit/$', 'merchant.views.customer_edit', name='customer_edit'),
    url(r'^users/$', 'merchant.views.users', name='users'),
    url(r'^user/new/$', 'merchant.views.user_new', name='user_new'),
    url(r'^user/profile/$', 'merchant.views.user_profile', name='user_profile'),

)
