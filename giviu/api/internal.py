from django.http import (HttpResponse, HttpResponseBadRequest)
from django.shortcuts import get_object_or_404
from giviu.models import Users, Product, Giftcard
from api.models import ApiClientId
from marketing import simple_giftcard_send_notification
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

    today = date.today()
    products = Product.objects.filter(
        send_date=today,
        already_sent=0,
    )

    gf_sent = []
    for product in products:
        gf_sent.append({
            'from': product.giftcard_from.email,
            'to': product.giftcard_to.email,
            'giftcard_id': product.giftcard.id,
            'price': product.price,
        })
        simple_giftcard_send_notification(product)

    data = {
        'status': 'success' if len(products) > 0 else 'no giftcards sent',
        'count': len(products),
        'send_date': today.isoformat(),
        'giftcards_sent': gf_sent,
    }

    return HttpResponse(json.dumps(data), content_type='application/json',
                        status=200)
