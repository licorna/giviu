from django.http import (HttpResponse, HttpResponseBadRequest)
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from django.conf import settings
from giviu.models import Product, Users, Giftcard
from api.models import ApiClientId
from landing.models import BetaRegisteredUser
from social.models import Likes
from marketing import (simple_giftcard_send_notification,
                       event_beta_registered_send_welcome,
                       marketing_send_marketing_monthly_birthday_nl)

from genderator.detector import Detector, MALE

from datetime import date, datetime
import random
import json
import logging
logger = logging.getLogger(__name__)


def send_giftcards_for_today(request):
    if not 'client_id' in request.GET:
        logger.critical('Internal API accessed with no client_id')
        return HttpResponseBadRequest()

    client_id = request.GET['client_id']
    api_client = get_object_or_404(ApiClientId,
                                   client_id=client_id,
                                   merchant__slug='giviu')

    just_check = request.GET.get('just_check', 'true') != 'false'

    today = date.today()
    products = Product.objects.filter(
        send_date=today,
        already_sent=0,
        state='RESPONSE_FROM_PP_SUCCESS'
    )

    gf_sent = []
    for product in products:
        gf_sent.append({
            'from': product.giftcard_from.email,
            'to': product.giftcard_to.email,
            'giftcard_id': product.giftcard.id,
            'giftcard': product.giftcard.title,
            'price': product.price,
        })
        if not just_check:
            simple_giftcard_send_notification(product)

    data = {
        'status': 'success' if len(products) > 0 else 'no giftcards sent',
        'count': len(products),
        'send_date': today.isoformat(),
        'giftcards_sent': gf_sent,
        'actually_sent': not just_check,
    }

    return HttpResponse(json.dumps(data), content_type='application/json',
                        status=200)


@require_GET
def send_welcome_to_beta_users(request):
    if 'client_id' not in request.GET:
        return HttpResponseBadRequest()

    just_check = request.GET.get('just_check', 'true') != 'false'

    client_id = request.GET['client_id']
    get_object_or_404(ApiClientId,
                      client_id=client_id,
                      merchant__slug='giviu')

    registered = BetaRegisteredUser.objects.all()
    if settings.DEBUG:
        registered = [registered[0]]

    email_list = []
    for user in registered:
        if not just_check:
            logger.info('Sending welcome email to ' + user.email)
            event_beta_registered_send_welcome(user.email)
        email_list.append(user.email)

    data = {
        'count': len(email_list),
        'recipients': email_list,
        'actually_sent': not just_check,
    }

    return HttpResponse(json.dumps(data), content_type='application/json',
                        status=200)


@require_GET
def send_marketing_monthly_birthday_nl(request):
    d = Detector()

    def is_male(full_name):
        return d.getGender(full_name.split()[0]) == MALE

    if 'client_id' not in request.GET:
        return HttpResponseBadRequest()

    just_check = request.GET.get('just_check', 'true') != 'false'
    just_try = request.GET.get('just_try', 'no')

    client_id = request.GET['client_id']
    get_object_or_404(ApiClientId,
                      client_id=client_id,
                      merchant__slug='giviu')

    if just_try != 'no':
        users = Users.objects.filter(email=just_try)
    else:
        users = Users.objects.filter(is_active=1,
                                     is_receiving=0,
                                     is_merchant=0)

    male_giftcards = Giftcard.objects.filter(gender='male',
                                             status=1).order_by('-priority')[:10]
    female_giftcards = Giftcard.objects.filter(gender='female',
                                               status=1).order_by('-priority')[:10]
    uni_giftcards = Giftcard.objects.filter(gender='both',
                                            status=1).order_by('-priority')[:10]

    if settings.DEBUG:
        users = users[:1]
    month = datetime.now().month
    email_list = []
    for user in users:
        friends = Likes.get_facebook_friends_birthdays(user.fbid, month)[:10]
        if len(friends) == 0:
            continue

        recommendations = []
        for friend in friends:
            recomendation_unisex = random.sample(uni_giftcards, 1)[0]
            if d.getGender(friend['first_name'].split()[0]) == MALE:
                recomendation_sex = random.sample(male_giftcards, 1)[0]
            else:
                recomendation_sex = random.sample(female_giftcards, 1)[0]
            friend['recommended'] = random.sample([recomendation_sex,
                                                   recomendation_unisex], 1)[0]
            recommendations.append({'name': friend['first_name'],
                                    'recommended': friend['recommended'].title,
                                    'birthday': friend['birthday'],
                                    'fbid': friend['fbid']})

        email_list.append({'email': user.email,
                           'friends': recommendations})

        if not just_check:
            marketing_send_marketing_monthly_birthday_nl(user, friends)
            #print 'just_check malo'

    data = {
        'count': len(users),
        'recipients': email_list,
        'actually_sent': not just_check,
    }
    return HttpResponse(json.dumps(data), content_type='application/json',
                        status=200)
