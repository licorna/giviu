from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponseBadRequest
from django.conf import settings
from giviu.models import PaymentTransaction
import django.core.exceptions.MultipleObjectsReturned
import random

if settings.DEVELOPMENT:
    from settings_development import *
else:
    from settings_production import *

def first_stage(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    if 'token' not in request.POST:
        return HttpResponseBadRequest()

    if 'trx_id' not in request.POST:
        return HttpResponseBadRequest()

    token = request.POST['token']
    trx_id = request.POST['trx_id']
    redirect_to = PUNTO_PAGOS_PHASE3_URL + '/transaccion/procesar/' + token
    redirect_head = '<meta http-equiv="refresh" content="10; %s" />'

    try:
        #TODO: Log
        payment = PaymentTransaction.objects.get(transaction_uuid=trx_id)
    except MultipleObjectsReturned:
        #TODO: Error grave
        pass

    last_state = payment.set_state('CLIENT_BEING_SENT_TO_PP')

    data = {
        'additional_head': redirect_head % (redirect_to, )
    }
    return render_to_response('success.html', data)
