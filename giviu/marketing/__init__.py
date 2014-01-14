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


def event_user_buy_product(email_from, email_to):
    '''This event gets triggered when the user buys a giftcard.'''
    pass
