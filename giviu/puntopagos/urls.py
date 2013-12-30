from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # phase4: notify
    url(r'^notify$', 'puntopagos.views.notify', name='puntopagos_notify'),
)
