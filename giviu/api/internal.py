from django.http import (HttpResponse, HttpResponseBadRequest)
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from django.conf import settings
from giviu.models import Product
from api.models import ApiClientId
from landing.models import BetaRegisteredUser
from marketing import (simple_giftcard_send_notification,
                       event_beta_registered_send_welcome)

from datetime import date
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

    print registered

    email_list = []
    for user in registered:
        print 'sending mail to:', user.email, '? ', 'no' if just_check else 'yes'
        if not just_check:
            event_beta_registered_send_welcome(user.email)
        email_list.append(user.email)

    data = {
        'count': len(email_list),
        'recipients': email_list,
        'actually_sent': not just_check,
    }

    return HttpResponse(json.dumps(data), content_type='application/json',
                        status=200)
