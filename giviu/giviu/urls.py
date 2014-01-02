from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'giviu.views.home', name='home'),
    url(r'^giftcard/detail/(?P<gift_id>\d+)$', 'giviu.views.giftcard_detail', name='giftcard_detail'),
    url(r'^giftcard/category/(?P<slug>[a-z-]+)$', 'giviu.views.home', name='giftcard_category'),
    url(r'^giftcard/custom/(?P<gift_id>\d+)$', 'giviu.views.giftcard_custom', name='giftcard_custom'),
    url(r'^logout$', 'giviu.views.do_logout', name='logout'),
    url(r'^register', 'giviu.views.do_register', name='register'),
    url(r'^giftcard/checkout$', 'giviu.views.giftcard_confirmation', name='giftcard_confirmation'),

    url(r'^giftcard/success$', 'giviu.views.giftcard_success', name='giftcard_success'),
    url(r'^giftcard/error$', 'giviu.views.giftcard_error', name='giftcard_error'),

    url(r'^user$', 'giviu.views.user', name='user'),
    url(r'^user/sent$', 'giviu.views.sent', name='user_sent'),
    url(r'^user/calendar$', 'giviu.views.calendar', name='user_calendar'),

    url(r'^api/', include('api.urls')),

    url(r'^merchant/', include('merchant.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^psp/', include('psp.urls')),
    url(r'^puntopagos/', include('puntopagos.urls')),
)
