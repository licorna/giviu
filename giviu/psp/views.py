from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
from giviu.models import PaymentTransaction, Product, CustomerInfo
from django.core.exceptions import MultipleObjectsReturned
from puntopagos import transaction_check
from django.template import RequestContext
from marketing import (event_merchant_notification_giftcard_was_bought,
                       event_user_buy_product_confirmation,
                       event_user_confirmation_sends_giftcard,
                       event_user_receives_product,
                       simple_giftcard_send_notification,
                       simple_giftcard_send_notification_auto_validate)
from merchant_notifications.signals import merchant_notification
from datetime import datetime
from credits import finalize_use_user_credits


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

    if 'product_id' not in request.POST:
        return HttpResponseBadRequest()

    trx_id = request.POST['trx_id']
    try:
        payment = PaymentTransaction.objects.get(transaction_uuid=trx_id)
        if payment.state == 'USING_CREDITS':
            payment.set_state('USING_CREDITS_SUCCESS')
            return redirect('/psp/success/' + payment.psp_token)
        else:
            payment.set_state('CLIENT_BEING_SENT_TO_PP')
    except PaymentTransaction.MultipleObjectsReturned:
        print 'multipleobjectreturned'
        #TODO: Error grave
        pass

    token = request.POST['token']
    # trx_id = request.POST['trx_id']
    redirect_to = PUNTO_PAGOS_PHASE3_URL + '/' + token
    redirect_head = '<meta http-equiv="refresh" content="4; %s" />'

    try:
        product = Product.objects.get(uuid=request.POST['product_id'])
    except Product.DoesNotExist:
        return HttpResponseBadRequest()

    product.set_state('WAITING_CONFIRMATION_FROM_PP')
    data = {
        'additional_head': redirect_head % (redirect_to, ),
    }
    return render_to_response('waiting.html', data)


@require_GET
def pp_response(request, token, **kwargs):
    status = kwargs.get('status', 'error') == 'success'
    try:
        transaction = PaymentTransaction.objects.get(psp_token=token)
        if transaction.is_closed():
            #TODO: La transaccion ya fue procesada, debe ser dirigido a
            #la pagina de checkout o la pagina de giftcards de usuarios.
            return redirect('/user')

    except PaymentTransaction.DoesNotExist:
        #TODO: Log
        return HttpResponseBadRequest()

    if transaction.state != 'USING_CREDITS_SUCCESS':
        status, response = transaction_check(
            token,
            transaction.transaction_uuid,
            transaction.amount,
            transaction.origin_timestamp
        )
        payment_method = response['medio_pago_descripcion']
        payment_total = response['monto']
        payment_date = response['fecha_aprobacion']
        payment_operation_number = response['numero_operacion']
        payment_authorization_code = response['codigo_autorizacion']
    else:
        import locale
        locale.setlocale(locale.LC_ALL, 'es_ES.utf-8')
        payment_method = 'Creditos'
        payment_total = '0'
        payment_date = datetime.strftime(datetime.now(), '%d %B, %Y')
        payment_operation_number = None
        payment_authorization_code = None
    try:
        product = Product.objects.get(transaction=transaction)
    except Product.DoesNotExist:
        #TODO: Esto no puede ocurrir, porque violaria una restriccion de MySQL
        return HttpResponseBadRequest()
    except Product.MultipleObjectsReturned:
        return HttpResponseBadRequest()
        #TODO: Error grave

    if status is True:
        if transaction.state == 'USING_CREDITS_SUCCESS':
            product.set_state('USING_CREDITS_SUCCESS')
            transaction.set_state('USING_CREDITS_SUCCESS')
        else:
            product.set_state('RESPONSE_FROM_PP_SUCCESS')
            transaction.set_state('RESPONSE_FROM_PP_SUCCESS')

        try:
            customer = CustomerInfo.objects.get(user=product.giftcard_to,
                                                merchant=product.giftcard.merchant)
        except CustomerInfo.DoesNotExist:
            customer = CustomerInfo(user=product.giftcard_to,
                                    merchant=product.giftcard.merchant)
            customer.save()

        args = {
            'payment_method': payment_method,
            'payment_total': payment_total,
            'payment_date': payment_date,
            'payment_operation_number': payment_operation_number,
        }
        transaction.operation_number = payment_operation_number
        transaction.authorization_code = payment_authorization_code

        if product.state != 'USING_CREDITS_SUCCESS':
            transaction.raw_response = response
            transaction.save()

        # Next block will send notification emails
        if not product.giftcard.auto_validate:
            # Merchant notification
            args0 = {
                'merchant_name': product.giftcard.merchant.name,
                'product_name': product.giftcard.title,
                'product_date': product.created.isoformat(),
            }
            event_merchant_notification_giftcard_was_bought(product.giftcard.merchant.contact_email, args0)
            _code = product.validation_code
            _code = _code[:4] + '-' + _code[4:]
            merchant_notification.send(sender=request,
                                       merchant=product.giftcard.merchant.id,
                                       code=_code,
                                       ammount=product.price)

            event_user_buy_product_confirmation(product.giftcard_from.email, args)
            now = datetime.now()
            if (product.send_date.year == now.year and
                product.send_date.month == now.month and
                product.send_date.day == now.day and
                not product.giftcard.auto_validate):

                simple_giftcard_send_notification(product)
        else:
            # Is auto_validation giftcard
            # FIXME: 'levantemos_chile' parameter needs to be taken
            # from somewhere else ;)
            simple_giftcard_send_notification_auto_validate('levantemos_chile',
                                                            product)

        data = {'product': product}
        if product.state == 'USING_CREDITS_SUCCESS':
            data.update({'used_credits': product.price})
        else:
            data.update({'transaction': response})

        if transaction.use_credits is not None:
            finalize_use_user_credits(transaction.use_credits)

        return render_to_response('success.html', data,
                                  context_instance=RequestContext(request))
    else:
        product.set_state('RESPONSE_FROM_PP_ERROR')
        transaction.set_state('RESPONSE_FROM_PP_ERROR')
        if transaction.use_credits is not None:
            finalize_use_user_credits(transaction.use_credits, False)
        data = {}
        return render_to_response('error.html', data,
                                  context_instance=RequestContext(request))
