from django.shortcuts import render, render_to_response
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from giviu.models import PaymentTransaction
import django.core.exceptions.MultipleObjectsReturned
import json

from django.conf import settings
if settings.DEVELOPMENT:
    from giviu.settings_development import *
else:
    from giviu.settings_production import *

@require_POST
def notify(request):
    '''
    PuntoPagos Phase4: Notify
    '''
    if 'Fecha' not in request.META or 'Autorizacion' not in request.META:
        return HttpResponseBadRequest()

    try:
        received = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest()

    my_auth = notify_check(
        received['token'],
        received['trx_id'],
        received['amount'],
        request.META['FECHA']
    )

    if 'trx_id' in received:
        try:
            payment = PaymentTransaction.object.get(transaction_uuid__exact=trx_id)
        except MultipleObjectsReturned:
            #TODO: Error y log
            pass
        #TODO: Validar que todos estos parametros se pasen como datos POST
        # Utilizando (puede ser) un frozenset y 'issubset'
        payment.operation_number = request.POST['numero_operacion']
        payment.authorization_code = request.POST['codigo_autorizacion']
        payment.set_state('NOTIFIED_BY_PP')
        payment.save()

    received_client_id, received_auth = request.META['Autorizacion'][3:].split(':')
    if received_auth != my_auth or received_client_id != PUNTO_PAGOS_CLIENTID:
        # TODO: Loguear problema
        return HttpResponseBadRequest()

    data = {
        'respuesta': '00',
        'token': received['token'],
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
