from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
from giviu.models import PaymentTransaction
from django.core.exceptions import MultipleObjectsReturned
from puntopagos import transaction_check

if settings.DEVELOPMENT:
    from giviu.settings_development import *
else:
    from giviu.settings_production import *


@require_POST
def first_stage(request):
    if settings.ENVIRONMENT == 'pretesting':
        return HttpResponse('Sitio de Pruebas')

    if 'token' not in request.POST:
        return HttpResponseBadRequest()

    if 'trx_id' not in request.POST:
        return HttpResponseBadRequest()

    token = request.POST['token']
    trx_id = request.POST['trx_id']
    redirect_to = PUNTO_PAGOS_PHASE3_URL + '/' + token
    redirect_head = '<meta http-equiv="refresh" content="4; %s" />'

    try:
        #TODO: Log
        payment = PaymentTransaction.objects.get(transaction_uuid=trx_id)
        last_state = payment.set_state('CLIENT_BEING_SENT_TO_PP')
    except MultipleObjectsReturned:
        print 'multipleobjectreturned'
        #TODO: Error grave
        pass

    data = {
        'additional_head': redirect_head % (redirect_to, )
    }
    return render_to_response('success.html', data)

@require_GET
def success(request, token):
    try:
        transaction = PaymentTransaction.objects.get(psp_token__exact=token)
    except PaymentTransaction.DoesNotExist:
        #TODO: Log
        return HttpResponseBadRequest()

    status, response = transaction_check(
        token,
        transaction.transaction_uuid,
        transaction.amount,
        transaction.origin_timestamp
    )

    if status is True:
        transaction.set_state('RESPONSE_FROM_PP_SUCCESS')
    else:
        transaction.set_state('RESPONSE_FROM_PP_ERROR')

    transaction.raw_response = response
    transaction.operation_number = response['numero_operacion']
    transaction.authorization_code = response['codigo_autorizacion']
    transaction.save()

    return HttpResponse('Este es el token siiii' + token)
