from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
from giviu.models import PaymentTransaction, Product, CustomerInfo
from django.core.exceptions import MultipleObjectsReturned
from puntopagos import transaction_check
from django.template import RequestContext
from marketing import event_merchant_notification_giftcard_was_bought


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

    try:
        product = Product.objects.get(uuid=request.POST['product_id'])
    except Product.DoesNotExist:
        return HttpResponseBadRequest()

    product.set_state('WAITING_CONFIRMATION_FROM_PP')

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
        'additional_head': redirect_head % (redirect_to, ),
    }
    return render_to_response('waiting.html', data)


@require_GET
def pp_response(request, token, **kwargs):
    status = kwargs.get('status', 'error') == 'success'
    try:
        transaction = PaymentTransaction.objects.get(psp_token__exact=token)
        if transaction.is_closed():
            #TODO: La transaccion ya fue procesada, debe ser dirigido a
            #la pagina de checkout o la pagina de giftcards de usuarios.
            return HttpResponse('Redirigir a /user/giftcard o algo')

    except PaymentTransaction.DoesNotExist:
        #TODO: Log
        return HttpResponseBadRequest()

    status, response = transaction_check(
        token,
        transaction.transaction_uuid,
        transaction.amount,
        transaction.origin_timestamp
    )

    try:
        product = Product.objects.get(transaction=transaction)
    except DoesNotExist:
        #TODO: Esto no puede ocurrir, porque violaria una restriccion de MySQL
        return HttpResponseBadRequest()
    except MultipleObjectsReturned:
        return HttpResponseBadRequest()
        #TODO: Error grave

    if status is True:
        product.set_state('RESPONSE_FROM_PP_SUCCESS')
        transaction.set_state('RESPONSE_FROM_PP_SUCCESS')

        # Send merchant notification
        # INPUT: merchant_email
        #        giftcard details
        args0 = {
            'merchant_name': product.giftcard.merchant.name,
            'product_name': product.giftcard.title,
            'product_date': product.created.isoformat(),
        }
        event_merchant_notification_giftcard_was_bought(merchant_email, args0)

        try:
            customer = CustomerInfo.objects.get(user=product.giftcard_to,
                                                merchant=product.giftcard.merchant)
        except CustomerInfo.DoesNotExist:
            customer = CustomerInfo(user=product.giftcard_to,
                                    merchant=product.giftcard.merchant)
            customer.save()

        args = {
            'payment_method': response['medio_pago_descripcion'],
            'payment_total': response['monto'],
            'payment_date': response['fecha_aprobacion'],
            'payment_operation_number': response['numero_operacion']
        }
        event_user_buy_product_confirmation(product.giftcard_from.email, args)
        transaction.operation_number = response['numero_operacion']
        transaction.authorization_code = response['codigo_autorizacion']

        now = datetime.now()
        if (product.send_date.year == now.year and
            product.send_date.month == now.month and
            product.send_date.day == now.day):

            args1 = {
                'name_from': product.giftcard_from.name,
                'name_to': product.giftcard_to.name,
            }
            event_user_confirmation_sends_giftcard(product.giftcard_from.email,
                                                   args1)
            args2 = {
                'product_code': product.uuid,
                'name_to': product.giftcard_to.name,
                'name_from': product.giftcard_from.name,
                'description': product.comment,
                'giftcard_design': product.design.image,
            }
            event_user_receives_product(product.giftcard_to, args2)
            product.already_sent = 1
            product.save()

        transaction.raw_response = response
        transaction.save()
        data = {
            'transaction' : response,
            'product' : product
        }
        return render_to_response('success.html', data,
                                  context_instance=RequestContext(request))
    else:
        product.set_state('RESPONSE_FROM_PP_ERROR')
        transaction.set_state('RESPONSE_FROM_PP_ERROR')
        data = {}
        return render_to_response('error.html',data,
                                  context_instance=RequestContext(request))



def prueba(request):
    data = {

    }
    return render_to_response('prueba.html')
