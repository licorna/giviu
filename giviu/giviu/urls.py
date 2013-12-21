from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'giviu.views.home', name='home'),
    url(r'^giftcard/detail/(?P<gift_id>\d+)$', 'giviu.views.giftcard_detail', name='giftcard_detail'),
    url(r'^giftcard/category/(?P<slug>\d+)$', 'giviu.views.giftcard_category', name='giftcard_category'),
    url(r'^giftcard/custom/(?P<gift_id>\d+)$', 'giviu.views.giftcard_custom', name='giftcard_custom'),
    url(r'^login$', 'giviu.views.do_login', name='login'),
    url(r'^logout$', 'giviu.views.do_logout', name='logout'),

    url(r'^admin/', include(admin.site.urls)),
)
