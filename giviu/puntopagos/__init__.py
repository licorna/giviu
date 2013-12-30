from hashlib import sha1
import hmac
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
from uuid import uuid4
import requests
from string import Template
from giviu.models import PaymentTransaction

from django.conf import settings
if settings.DEVELOPMENT:
    from giviu.settings_development import *
else:
    from giviu.settings_production import *


def now_rfc1123():
    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)


def authorization_header(trx_id, amount):
    assert isinstance(amount, str)

    date = now_rfc1123()
    message = Template('transaccion/crear\n$trx_id\n$amount\n$date')
    message = message.substitute(trx_id=trx_id,
                                 amount=amount,
                                 date=date)

    digest = hmac.new(PUNTO_PAGOS_SECRET, message)
    return 'PP %s:%s' % (PUNTO_PAGOS_CLIENTID, digest)


def get_punto_pago_payment_method():
    return PUNTO_PAGOS_PMETHOD


def transaction_create(amount):
    trx_id = str(uuid4())
    current_datetime = now_rfc1123()
    auth_header = authorization_header(trx_id, amount)
    medio_pago = get_punto_pago_payment_method()

    payment = PaymentTransaction(
        transaction_uuid = trx_id,
        origin_timestamp = current_datetime,
        auth_header = auth_header,
        payment_method = medio_pago,
        amount = amount
    )
    payment.save()

    headers = {
        'Fecha': current_datetime,
        'Autorizacion': auth_header
    }
    data = json.dumps({
        'trx_id': trx_id,
        'medio_pago': medio_pago,
        'monto': amount,
    })

    #TODO: Loguear envio
    response = requests.post(PUNTO_PAGOS_PHASE1_URL, data=data, headers=headers)
    #TODO: Loguear recibo

    #TODO: if response.status == 200: ?!?
    response = json.loads(response.body)
    try:
        token = response['token']
        payment.psp_token = token
        payment.save()
    except KeyError:
        #TODO: patalear
        pass
    payment.set_state('CREATED_IN_PP')

    return response


def notify_check(token, trx_id, amount, date):
    message = Template('transaccion/notificacion\n$token\n$trx\n$amount\n$date').substitute(
        token=token,
        trx=trx_id,
        amount=amount,
        date=date)

    return hmac.new(PUNTO_PAGOS_SECRET, message)
