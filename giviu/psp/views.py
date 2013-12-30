from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.conf import settings
from giviu.models import PaymentTransaction
from django.core.exceptions import MultipleObjectsReturned

import random

if settings.DEVELOPMENT:
    from giviu.settings_development import *
else:
    from giviu.settings_production import *

@require_POST
def first_stage(request):
    if 'token' not in request.POST:
        return HttpResponseBadRequest()

    if 'trx_id' not in request.POST:
        return HttpResponseBadRequest()

    token = request.POST['token']
    trx_id = request.POST['trx_id']
    redirect_to = PUNTO_PAGOS_PHASE3_URL + '/transaccion/procesar/' + token
    redirect_head = '<meta http-equiv="refresh" content="4; %s" />'

    try:
        #TODO: Log
        payment = PaymentTransaction.objects.get(transaction_uuid=trx_id)
        last_state = payment.set_state('CLIENT_BEING_SENT_TO_PP')
    except MultipleObjectsReturned:
        #TODO: Error grave
        pass

    data = {
        'additional_head': redirect_head % (redirect_to, )
    }
    return render_to_response('success.html', data)
