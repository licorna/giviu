# -*- coding: utf-8 -*-

from django.core.mail import EmailMultiAlternatives
from django.core.mail.message import EmailMessage
from django.template import Context
from django.template.loader import get_template
from django.conf import settings
from marketing.models import EmailTemplate
from json import dumps
from datetime import datetime


def event_sent_giftcards_for_today(content):
    '''This event will trigger when giftcards for today are sent'''
    today = datetime.now().strftime('%Y-%m-%d')
    if settings.DEBUG:
        email = [settings.DEBUG_EMAIL_RECEIVER]
    else:
        email = [x[1] for x in settings.GIVIU_FOUNDERS]
    print 'sending to ' + str(email)
    msg = EmailMessage()
    msg.subject = 'Giftcards Sent ' + today
    msg.body = 'Please find attached Giftcards Sent Today'
    msg.from_email = settings.EMAIL_DEFAULT_FROM
    msg.to = email
    msg.attach(filename='data.json',
               mimetype='application/json',
               content=dumps(content))
    msg.send()


def event_user_registered(email, name):
    '''This event triggers when the user registers.'''
    c = Context({'name': name})
    html_content = get_template('marketing_welcome.html').render(c)
    text_content = get_template('marketing_welcome.text').render(c)
    if settings.DEBUG:
        email = settings.DEBUG_EMAIL_RECEIVER
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
        email = settings.DEBUG_EMAIL_RECEIVER
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
        email = settings.DEBUG_EMAIL_RECEIVER
    msg = EmailMultiAlternatives(subject,
                                 text_content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def event_remember_user_forgotten_giftcard(product):
    '''This email is sent when a user forgot to validate his
    giftcard and need to do it before it expires.'''
    email = product.giftcard_to.email
    c = Context({
        'giftcard_design': product.design.image,
        'name_from': product.giftcard_from.get_full_name(),
        'validation_code': product.get_validation_code(),
        'giftcard_image': product.giftcard.image,
        'giftcard_amount': product.price if product.giftcard.kind == '1' else None,
        'merchant_name': product.giftcard.merchant.name,
        'giftcard_name': product.giftcard.title,
        'validation_info': product.giftcard.get_validation_info()
    })

    subject = '¡Tienes una giftcard sin validar en Giviu!'
    html_content = get_template('marketing_remember_giftcard.html').render(c)
    if settings.DEBUG:
        email = settings.DEBUG_EMAIL_RECEIVER
    msg = EmailMultiAlternatives(subject,
                                 html_content,
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
        'validation_info': product.giftcard.get_validation_info(),
        'validation_code': product.get_validation_code(),
        'merchant_name': product.giftcard.merchant.name,
        'giftcard_name': product.giftcard.title,
        'giftcard_image': product.giftcard.image,
        'giftcard_amount': product.price if product.giftcard.kind == '1' else None,
    }
    event_user_receives_product(product.giftcard_to.email, args2)
    product.already_sent = 1
    product.save()

    return True


def simple_giftcard_send_notification_auto_validate(template, product):
    template = EmailTemplate.objects.get(name=template)
    email = product.giftcard_from.email

    c = Context({})
    html_content = get_template(template.html_template).render(c)
    text_content = get_template(template.text_template).render(c)
    subject = template.subject.format(**locals())
    if settings.DEBUG:
        email = settings.DEBUG_EMAIL_RECEIVER
    msg = EmailMultiAlternatives(subject,
                                 text_content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def event_user_confirmation_sends_giftcard(email, args):
    '''This event triggers when a giftcard a users bought is send to
    the destination party.'''
    c = Context(args)
    html_content = get_template('marketing_sender_notification.html').render(c)
    text_content = get_template('marketing_sender_notification.html').render(c)
    subject = 'La giftcard regalada a ' + args['name_to'] + ' ha sido enviada'
    if settings.DEBUG:
        email = settings.DEBUG_EMAIL_RECEIVER
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
        email = settings.DEBUG_EMAIL_RECEIVER
    msg = EmailMultiAlternatives('Has vendido una giftcard',
                                 text_content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def event_beta_registered_send_welcome(email):
    c = Context({})
    html_content = get_template('marketing_first.html').render(c)
    text_content = get_template('marketing_first.html').render(c)
    if settings.DEBUG:
        email = settings.DEBUG_EMAIL_RECEIVER
    msg = EmailMultiAlternatives('¡Ven a conocer Giviu!',
                                 text_content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def marketing_send_marketing_monthly_birthday_nl(user, friends):
    c = Context({
        'user': user,
        'friends': friends,
    })
    html_content = get_template('marketing_birthday.html').render(c)
    text_content = html_content
    if settings.DEBUG:
        email = settings.DEBUG_EMAIL_RECEIVER
    else:
        email = user.email
    msg = EmailMultiAlternatives(user.first_name + ', te ayudamos con los regalos de este mes.',
                                 text_content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def marketing_send_daily_birthday(user, friends):
    c = Context({
        'user': user,
        'friends': friends,
    })

    html_content = get_template('marketing_birthday.html').render(c)
    text_content = html_content
    if settings.DEBUG:
        email = settings.DEBUG_EMAIL_RECEIVER
    else:
        email = user.email

    if len(friends) == 0:
        return
    if len(friends) == 1:
        subject = friends[0]['first_name'] + u' está de cumpleaños y te recomendamos qué regalarle'
    if len(friends) == 2:
        subject = friends[0]['first_name'] + u' y ' + friends[1]['first_name'] + u' están de cumpleaños y te recomendamos qué regalarles'
    if len(friends) > 2:
        subject = friends[0]['first_name'] + ' y otros ' + str(len(friends) - 1) + u' amigos están de cumpleaños hoy y te recomendamos qué regalarles'

    msg = EmailMultiAlternatives(subject,
                                 text_content,
                                 settings.EMAIL_DEFAULT_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
