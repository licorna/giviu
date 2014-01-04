from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'landing.views.home', name='landing_home'),
    url(r'^giftcard/detail/(?P<gift_id>\d+)$', 'giviu.views.giftcard_detail', name='giftcard_detail'),
    url(r'^giftcard/category/(?P<slug>[a-z-]+)$', 'giviu.views.home', name='giftcard_category'),
    url(r'^giftcard/custom/(?P<gift_id>\d+)$', 'giviu.views.giftcard_custom', name='giftcard_custom'),
    url(r'^logout$', 'giviu.views.do_logout', name='logout'),
    url(r'^register', 'giviu.views.do_register', name='register'),
    url(r'^giftcard/checkout$', 'giviu.views.giftcard_confirmation', name='giftcard_confirmation'),
    url(r'^product/show/(?P<uuid>\S+)$', 'giviu.views.product_show', name='product_show'),

    # url(r'^giftcard/success$', 'giviu.views.giftcard_success', name='giftcard_success'),

    url(r'^user$', 'giviu.views.user', name='user'),
    url(r'^user/sent$', 'giviu.views.sent', name='user_sent'),
    url(r'^user/calendar$', 'giviu.views.calendar', name='user_calendar'),

    url(r'^partner/(?P<merchant_slug>\S+)$', 'giviu.views.partner_info', name='partner_info'),

    url(r'^page/giviu$', 'giviu.views.page_who_we_are', name='page_who_we_are'),
    url(r'^page/como-funciona$', 'giviu.views.page_who_its_work', name='page_who_its_work'),
    url(r'^page/preguntas-frecuentes$', 'giviu.views.page_faq', name='page_faq'),
    url(r'^page/empresas$', 'giviu.views.page_enterprise', name='page_enterprise'),
    url(r'^page/contacto$', 'giviu.views.page_contact', name='page_contact'),
    url(r'^page/terminos-y-condiciones$', 'giviu.views.page_terms', name='page_terms'),

    url(r'^api/', include('api.urls')),
    url(r'^status/', include('status.urls')),

    url(r'^merchant/', include('merchant.urls')),

    url(r'^l/', include('landing.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^psp/', include('psp.urls')),
    url(r'^puntopagos/', include('puntopagos.urls')),
)
