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
                       marketing_send_marketing_monthly_birthday_nl,
                       marketing_send_daily_birthday)

from genderator.detector import Detector, MALE
import locale
from external_codes import add_external_codes_for_giftcard
from relevance import (get_relevant_giftcard_for_friend,
                       get_saved_recommendations,
                       store_current_recommendations)

from datetime import date, datetime, timedelta
import calendar
import random
import json
import logging
logger = logging.getLogger(__name__)


def send_giftcards_for_today(request):
    if not 'client_id' in request.GET:
        logger.critical('Internal API accessed with no client_id')
        return HttpResponseBadRequest()

    client_id = request.GET['client_id']
    get_object_or_404(ApiClientId,
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
def send_marketing_daily_birthday_nl(request):
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

    now = datetime.today()
    response = []
    count = 1
    for user in users:
        print 'Procesando amigo', count, 'de', len(users)
        count += 1
        friends = get_saved_recommendations(user)
        if not friends:
            friends = Likes.get_facebook_friends_birthdays(user.fbid,
                                                           now.month,
                                                           now.day)
            if not friends:
                continue
            for friend in friends:
                gf = Giftcard.objects.get(id=get_relevant_giftcard_for_friend(friend))
                friend['recommended'] = {
                    'id': gf.id,
                    'title': gf.title,
                    'slug': 'https://www.giviu.com' + gf.get_absolute_url(),
                    'image': gf.image,
                    'description': gf.description,
                }
            store_current_recommendations(friends, user)

        if len(friends) == 0:
            continue

        response.append({user.fbid: {
            'name': user.first_name,
            'date': now.strftime('%m/%d/%Y'),
            'friends': friends}})

        if not just_check:
            marketing_send_daily_birthday(user, friends)

    return HttpResponse(json.dumps(response), content_type='application/json',
                        status=200)


@require_GET
def send_marketing_monthly_birthday_nl(request):
    d = Detector()
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.utf-8')
    except:
        logger.error('Unable to set es_ES.utf-8 locale')

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

    now = datetime.now()
    month_name = datetime.strftime(now, '%B')
    email_list = []
    for user in users:
        friends = Likes.get_facebook_friends_birthdays(user.fbid, now.month)[:10]
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
                                    'birthday': friend['birthday'][3:5] +
                                    ' de ' +
                                    month_name,
                                    'fbid': friend['fbid']})

            friend['birthday'] = friend['birthday'][3:5] + ' de ' + month_name

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


def add_external_codes(request, giftcard):
    get_object_or_404(Giftcard, id=giftcard)
    just_check = request.GET.get('just_check', 'true') != 'false'

    external_codes = json.loads(request.body)
    if just_check is not False:
        add_external_codes_for_giftcard(int(giftcard), external_codes)

    return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json',
                        status=200)


def sold_giftcards_for_period(request):
    client_id = request.GET.get('client_id', None)
    get_object_or_404(ApiClientId,
                      client_id=client_id,
                      merchant__slug='giviu')

    now = datetime.now()
    date_from = request.GET.get('from', None)
    date_to = request.GET.get('to', None)

    if not date_from:
        date_from = datetime(year=now.year, month=now.month, day=1)
    else:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
        except ValueError:
            return HttpResponseBadRequest('Unparseable from')

    if not date_to:
        last_day = calendar.monthrange(now.year, now.month)[1]
        date_to = datetime(year=now.year, month=now.month, day=last_day)
    else:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            return HttpResponseBadRequest('Unparseable to')

    if date_from > date_to:
        return HttpResponseBadRequest('From date > To date')

    day1 = timedelta(days=1)
    date_to += day1  # date_to should be inclusive
    products = Product.objects.filter(created__range=(date_from,
                                                      date_to),
                                      state__regex='SUCCESS$')

    data = []
    for product in products:
        data.append({
            'price': product.price,
            'merchant_name': product.giftcard.merchant.name,
            'merchant_id': product.giftcard.merchant.id
        })

    return HttpResponse(json.dumps(data), content_type='application/json',
                        status=200)


def validated_giftcards_for_period(request):
    client_id = request.GET.get('client_id', None)
    get_object_or_404(ApiClientId,
                      client_id=client_id,
                      merchant__slug='giviu')

    now = datetime.now()
    date_from = request.GET.get('from', None)
    date_to = request.GET.get('to', None)

    if not date_from:
        date_from = datetime(year=now.year, month=now.month, day=1)
    else:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
        except ValueError:
            return HttpResponseBadRequest('Unparseable from')

    if not date_to:
        last_day = calendar.monthrange(now.year, now.month)[1]
        date_to = datetime(year=now.year, month=now.month, day=last_day)
    else:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            return HttpResponseBadRequest('Unparseable to')

    if date_from > date_to:
        return HttpResponseBadRequest('From date > To date')

    day1 = timedelta(days=1)
    date_to += day1  # date_to should be inclusive
    products = Product.objects.filter(validation_date__range=(date_from,
                                                              date_to),
                                      validated=True)

    data = []
    for product in products:
        data.append({
            'price': product.price,
            'merchant_name': product.giftcard.merchant.name,
            'merchant_id': product.giftcard.merchant.id
        })

    return HttpResponse(json.dumps(data), content_type='application/json',
                        status=200)
