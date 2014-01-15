from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from django.conf import settings


def event_user_registered(email, name):
    '''This event triggers when the user registers.'''
    c = Context({'name': name})
    html_content = get_template('marketing_welcome.html').render(c)
    text_content = get_template('marketing_welcome.text').render(c)
    if settings.DEBUG:
        email = 'licorna@gmail.com'
    msg = EmailMultiAlternatives('Bienvenido a Giviu',
                                 text_content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def event_user_buy_product_confirmation(email, args):
    '''This event gets triggered when the user buys a giftcard.
    At the same time he sees the Purchase Confirmation page.'''
    c = Context(args)
    html_content = get_template('marketing_buy_confirmation.html').render(c)
    text_content = get_template('marketing_buy_confirmation.html').render(c)
    if settings.DEBUG:
        email = 'licorna@gmail.com'
    msg = EmailMultiAlternatives('Confirmacion de compra en Giviu',
                                 text_content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def event_user_receives_product(email, args):
    '''This is the email a receiving users gets when he receives
    a giftcard indicating on how to proceed.'''
    c = Context(args)
    html_content = get_template('marketing_giftcard.html').render(c)
    text_content = get_template('marketing_giftcard.html').render(c)
    subject = 'Has recibido una giftcard de ' + args['name_from']
    if settings.DEBUG:
        email = 'licorna@gmail.com'
    msg = EmailMultiAlternatives(subject,
                                 text_content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def simple_giftcard_send_notification(product):
    '''This wrapper function will send both buyer and
    receiving parties the corresponding mailing when
    requested, and the given product will be marked
    as already_sent'''
    args1 = {
        'name_from': product.giftcard_from.get_full_name(),
        'name_to': product.giftcard_to.get_full_name(),
    }
    event_user_confirmation_sends_giftcard(product.giftcard_from.email,
                                           args1)

    args2 = {
        'product_code': product.uuid,
        'name_to': product.giftcard_to.get_full_name(),
        'name_from': product.giftcard_from.get_full_name(),
        'description': product.comment,
        'giftcard_design': product.design.image,
    }
    event_user_receives_product(product.giftcard_to.email, args2)
    product.already_sent = 1
    product.save()

    return True


def event_user_confirmation_sends_giftcard(email, args):
    '''This event triggers when a giftcard a users bought is send to
    the destination party.'''
    c = Context(args)
    html_content = get_template('marketing_sender_notification.html').render(c)
    text_content = get_template('marketing_sender_notification.html').render(c)
    subject = 'La giftcard regalada a ' + args['name_to'] + ' ha sido enviada'
    if settings.DEBUG:
        email = 'licorna@gmail.com'
    msg = EmailMultiAlternatives(subject,
                                 text_content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def event_merchant_notification_giftcard_was_bought(email, args):
    '''This event triggers when a users buys a giftcard. At the same time
    the user receives the Purchase Confirmation email, the merchant gets
    this email confirming a new Giftard was bought.'''
    c = Context(args)
    html_content = get_template('marketing_merchant_notification.html').render(c)
    text_content = get_template('marketing_merchant_notification.html').render(c)
    if settings.DEBUG:
        email = 'licorna@gmail.com'
    msg = EmailMultiAlternatives('Has vendido una giftcard',
                                 text_content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
