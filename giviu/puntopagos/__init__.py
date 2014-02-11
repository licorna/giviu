from hashlib import sha1
import hmac
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import base64
import requests
from string import Template
import json
from string import digits
import random
import logging
logger = logging.getLogger(__name__)

from django.conf import settings
if settings.DEVELOPMENT:
    from giviu.settings_development import *
else:
    from giviu.settings_production import *


def get_normalized_amount(amount):
    assert isinstance(amount, basestring)

    if amount[-3:] == '.00':
        return amount.strip()

    if '.' in amount:
        amount = amount.split('.')
        return amount[0] + '.' + amount[1][:2]

    return amount.strip() + '.00'


def now_rfc1123():
    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)


def authorization_header(trx_id, amount, date):

    message = Template('transaccion/crear\n$trx_id\n$amount\n$date')
    message = message.substitute(trx_id=trx_id,
                                 amount=amount,
                                 date=date)

    print 'message a enviar', message
    digest = base64.b64encode(hmac.new(PUNTO_PAGOS_SECRET, message, sha1).digest())
    return 'PP %s:%s' % (PUNTO_PAGOS_CLIENTID, digest)


def authorization_header_phase5(token, trx_id, amount, date):
    message = Template('transaccion/traer\n$token\n$trx_id\n$amount\n$date')
    message = message.substitute(token=token,
                                 trx_id=trx_id,
                                 amount=amount,
                                 date=date)

    digest = base64.b64encode(hmac.new(PUNTO_PAGOS_SECRET, message, sha1).digest())
    return 'PP %s:%s' % (PUNTO_PAGOS_CLIENTID, digest)


def get_punto_pago_payment_method():
    return PUNTO_PAGOS_PMETHOD


def transaction_create(amount):
    '''
    This method corresponds to the phase1 on the PuntoPagos
    documentation. It should be called just before redirecting
    the user to PuntoPagos end.
    Will return (as phase2 documentation states), a unique
    transaction identifier inside a bigger JSON response object.

    It starts creating a unique identifier from Giviu end to
    Punto Pagos. From now, the transaction will have a unique
    identifier from our side, 'trx_id' and a unique identifier
    from Punto Pagos side, 'token'.
    '''
    amount = get_normalized_amount(amount)
    trx_id = ''.join(random.sample(digits, 10))
    current_datetime = now_rfc1123()
    auth_header = authorization_header(trx_id, amount, current_datetime)
    payment_method = get_punto_pago_payment_method()

    payment = PaymentTransaction(
        transaction_uuid=trx_id,
        origin_timestamp=current_datetime,
        auth_header=auth_header,
        payment_method=payment_method,
        amount=amount
    )
    payment.save()

    headers = {
        'Fecha': current_datetime,
        'Autorizacion': auth_header,
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json'
    }

    data = '''{"trx_id":%s,"medio_pago":"%s","monto":%s}'''
    data = data % (trx_id, payment_method, amount)

    #TODO: Loguear envio
    print 'data to be sent', data
    print 'headers', headers
    response = requests.post(PUNTO_PAGOS_PHASE1_URL, data=data, headers=headers)
    print response.text
    #TODO: Loguear recibo

    #TODO: if response.status == 200: ?!?
    response = json.loads(response.text)
    try:
        token = response['token']
        payment.psp_token = token
        payment.save()
    except KeyError:
        #TODO: patalear
        pass
    payment.set_state('CREATED_IN_PP')

    return response, payment


def notify_check(token, trx_id, amount, date):
    message = Template('transaccion/notificacion\n$token\n$trx\n$amount\n$date')
    message = message.substitute(token=token,
                                 trx=trx_id,
                                 amount=amount,
                                 date=date)

    return base64.b64encode(hmac.new(PUNTO_PAGOS_SECRET, message).digest())


def transaction_check(token, trx_id, amount, date):
    '''
    Transaction Check corresponds to the phase 6 of the Non-SSL
    documentation. In this scenario the local business (Giviu)
    won't be notified about the state of the transaction, but it
    will have to pull this information from the server, once
    the transaction comes back redirected from Punto Pagos.
    '''
    amount = get_normalized_amount(amount)
    date = now_rfc1123()
    authorization = authorization_header_phase5(token, trx_id, amount, date)
    headers = {
        'Fecha': date,
        'Autorizacion': authorization,
        'Accept': 'application/json'
    }

    payment = PaymentTransaction.objects.get(psp_token__exact=token)
    payment.set_state('INFO_REQUESTED_TO_PP')

    r = requests.get(PUNTO_PAGOS_PHASE5_URL + token, headers=headers)
    try:
        response = json.loads(r.text)
    except ValueError:
        logger.critical('Unable to decode JSON data received from PP. Token:' + token)
        return False, {}

    return response['respuesta'] == '00', response
