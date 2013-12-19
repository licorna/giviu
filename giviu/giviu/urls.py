from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'giviu.views.home', name='home'),
    url(r'^giftcard/detail/(?P<gift_id>\d+)$', 'giviu.views.giftcard_detail', name='giftcard_detail'),
    url(r'^giftcard/category/(?P<slug>[a-z-]+)$', 'giviu.views.giftcard_category', name='giftcard_category'),


    url(r'^admin/', include(admin.site.urls)),

)
