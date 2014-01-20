from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^version$', 'api.views.version',
                           name='api_version'),

                       url(r'^users/exists-by-fb/(?P<fbid>\d+)$',
                           'api.views.user_exists_by_fbid',
                           name='api_users_exists_by_fb'),

                       url(r'^validate/giftcard/(?P<giftcard>[a-z0-9-]+)$',
                           'api.views.validate_giftcard',
                           name='api_validate_giftcard'),

                       url(r'^merchant/get-sales-by-giftcard/(?P<merchant_id>\d+)$',
                           'api.views.get_sales_by_service',
                           name='api_sales_by_service'),

                       url(r'^likes/add/(?P<user>\d+)/(?P<giftcard>\d+)$',
                           'api.views.add_gf_like',
                           name='api_social_like_add'),

                       url(r'^likes/get-from-friends/(?P<user>\d+)/(?P<giftcard>\d+)$',
                           'api.views.get_gf_like',
                           name='api_social_like_get'),

                       url(r'^social/add-user-from-facebook/(?P<fbid>\d+)$',
                           'api.views.add_user_from_facebook',
                           name='api_social_add_user_from_facebook'),

                       url(r'^social/add-friends-from-facebook/(?P<fbid>\d+)$',
                           'api.views.add_friends_from_facebook',
                           name='api_social_add_friends_from_facebook'),

                       url(r'^social/get-facebook-friends-birthdays/(?P<fbid>\d+)$',
                           'api.views.get_facebook_friends_birthdays'),

                       url(r'^social/add-close-facebook-friend/(?P<fbid>\d+)/(?P<friend>\d+)$',
                           'api.views.add_close_facebook_friend'),

                       url(r'^social/get-close-facebook-friends/(?P<fbid>\d+)$',
                           'api.views.get_close_facebook_friends'),

                       url(r'^internal/send-giftcards-for-today/$',
                           'api.internal.send_giftcards_for_today'),

                       url(r'^internal/send-welcome-to-beta-users/$',
                           'api.internal.send_welcome_to_beta_users'),
)
