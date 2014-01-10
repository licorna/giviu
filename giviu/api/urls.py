from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^version$', 'api.views.version', name='api_version'),
    url(r'^users/exists-by-fb/(?P<fbid>\d+)$', 'api.views.user_exists_by_fbid', name='api_users_exists_by_fb'),
    url(r'^validate/giftcard/(?P<giftcard>[a-z0-9-]+)$', 'api.views.validate_giftcard', name='api_validate_giftcard'),
    url(r'^merchant/get-sales-by-giftcard/(?P<merchant_id>\d+)$', 'api.views.get_sales_by_service', name='api_sales_by_service')
)
